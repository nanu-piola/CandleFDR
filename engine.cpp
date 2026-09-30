#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <unordered_map>
#include <cmath>
#include <algorithm>
#include <iomanip>

struct PatternStats {
    std::string pattern_id;
    int count = 0;
    double sum_ret = 0.0;
    double sq_sum_ret = 0.0;
    double mean_ret = 0.0;
    double std_dev = 0.0;
    double t_stat = 0.0;
    double p_value = 0.0;
    bool survives_fdr = false;
};

// Aproximación de la función de distribución acumulada normal estándar (CDF)
double normalCDF(double x) {
    return 0.5 * std::erfc(-x / std::sqrt(2.0));
}

// Cálculo del p-value para un t-test de dos colas
double calculate_p_value(double t_stat) {
    double tail = 1.0 - normalCDF(std::abs(t_stat));
    return 2.0 * tail;
}

int main() {
    std::ifstream file("tokens_data.csv");
    if (!file.is_open()) {
        std::cerr << "Error: No se pudo abrir tokens_data.csv" << std::endl;
        return 1;
    }

    std::string line;
    std::getline(file, line); // Saltear encabezado

    std::vector<int> tokens;
    std::vector<double> returns_1d;

    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string tok_str, ret1_str, ret3_str, ret5_str;

        if (std::getline(ss, tok_str, ',') && std::getline(ss, ret1_str, ',')) {
            tokens.push_back(std::stoi(tok_str));
            returns_1d.push_back(std::stod(ret1_str));
        }
    }
    file.close();

    std::cout << "Cargados " << tokens.size() << " registros." << std::endl;

    // Calcular el benchmark global (media y desviación del mercado)
    double global_sum = 0.0;
    for (double r : returns_1d) global_sum += r;
    double global_mean = global_sum / returns_1d.size();

    // Minería de 3-gramas (secuencias de 3 velas)
    const int N = 2;
    std::unordered_map<std::string, PatternStats> patterns;

   for (size_t i = 0; i <= tokens.size() - N - 1; ++i) {
    std::string pattern_key = std::to_string(tokens[i]) + "-" +
                              std::to_string(tokens[i+1]);
    
    double fwd_return = returns_1d[i + N - 1];

    auto& stat = patterns[pattern_key];
    stat.pattern_id = pattern_key;
    stat.count++;
    stat.sum_ret += fwd_return;
    stat.sq_sum_ret += fwd_return * fwd_return;
}

    std::vector<PatternStats> results;
    results.reserve(patterns.size());

    // Filtrar patrones con pocas ocurrencias (mínimo 10 muestras)
    for (auto& [key, stat] : patterns) {
        if (stat.count >= 5) {
            stat.mean_ret = stat.sum_ret / stat.count;
            
            double variance = (stat.sq_sum_ret / stat.count) - (stat.mean_ret * stat.mean_ret);
            stat.std_dev = std::sqrt(std::max(0.0, variance));

            if (stat.std_dev > 0.0) {
                // Standard error y t-statistic contra la media global
                double se = stat.std_dev / std::sqrt(stat.count);
                stat.t_stat = (stat.mean_ret - global_mean) / se;
                stat.p_value = calculate_p_value(stat.t_stat);
                results.push_back(stat);
            }
        }
    }

    // Ordenar resultados por p-value ascendente (requerido para Benjamini-Hochberg)
    std::sort(results.begin(), results.end(), [](const PatternStats& a, const PatternStats& b) {
        return a.p_value < b.p_value;
    });

    // Aplicar Benjamini-Hochberg FDR (False Discovery Rate q = 0.05)
    double q_threshold = 0.05;
    size_t m = results.size();
    int significant_count = 0;

    for (size_t i = 0; i < m; ++i) {
        double bh_critical = ((double)(i + 1) / m) * q_threshold;
        if (results[i].p_value <= bh_critical) {
            results[i].survives_fdr = true;
            significant_count++;
        }
    }

    // Mostrar Top 10 Patrones con mayor significancia estadística
    std::cout << "\n=== RESULTADOS DEL MOTOR DE MINERÍA DE PATRONES ===" << std::endl;
    std::cout << "Total de 3-gramas analizados: " << patterns.size() << std::endl;
    std::cout << "Patrones evaluados (count >= 10): " << m << std::endl;
    std::cout << "Patrones estadísticamente significativos (FDR q=0.05): " << significant_count << "\n" << std::endl;

    std::cout << std::left << std::setw(15) << "Patrón"
              << std::setw(10) << "Ocurrencias"
              << std::setw(15) << "Retorno Medio"
              << std::setw(12) << "t-stat"
              << std::setw(12) << "p-value"
              << std::setw(10) << "FDR Pass" << std::endl;
    std::cout << std::string(74, '-') << std::endl;

    for (size_t i = 0; i < std::min(size_t(15), results.size()); ++i) {
        std::cout << std::left << std::setw(15) << results[i].pattern_id
                  << std::setw(10) << results[i].count
                  << std::setw(15) << (std::to_string(results[i].mean_ret * 100).substr(0, 6) + "%")
                  << std::setw(12) << std::to_string(results[i].t_stat).substr(0, 5)
                  << std::setw(12) << std::to_string(results[i].p_value).substr(0, 6)
                  << std::setw(10) << (results[i].survives_fdr ? "SÍ" : "NO") << std::endl;
    }

    return 0;
}