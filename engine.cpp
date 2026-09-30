#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <map>
#include <cmath>
#include <algorithm>

struct PatternStat {
    std::string pattern_id;
    int count = 0;
    double sum_ret = 0.0;
    double sq_sum_ret = 0.0;
    double mean_ret = 0.0;
    double t_stat = 0.0;
    double p_value = 1.0;
    bool survives_fdr = false;
};

// P-value preciso usando erfc
double calculate_p_value(double t) {
    if (t == 0.0) return 1.0;
    double abs_t = std::abs(t);
    return std::erfc(abs_t / std::sqrt(2.0));
}

int main() {
    std::ifstream file("tokens_data.csv");
    if (!file.is_open()) {
        std::cerr << "Error: No se pudo abrir tokens_data.csv" << std::endl;
        return 1;
    }

    std::string line, token_str, ret_str;
    std::getline(file, line); // Header

    std::vector<int> tokens;
    std::vector<double> returns;

    while (std::getline(file, line)) {
        std::stringstream ss(line);
        if (std::getline(ss, token_str, ',') && std::getline(ss, ret_str, ',')) {
            tokens.push_back(std::stoi(token_str));
            returns.push_back(std::stod(ret_str));
        }
    }
    file.close();

    const int N = 2; // 2-gramas
    std::map<std::string, PatternStat> patterns;

    if (tokens.size() >= static_cast<size_t>(N + 1)) {
        for (size_t i = 0; i <= tokens.size() - N - 1; ++i) {
            std::string key = std::to_string(tokens[i]) + "-" + std::to_string(tokens[i+1]);
            double fwd_return = returns[i + N - 1];

            auto& stat = patterns[key];
            stat.pattern_id = key;
            stat.count++;
            stat.sum_ret += fwd_return;
            stat.sq_sum_ret += fwd_return * fwd_return;
        }
    }

    std::vector<PatternStat> evaluated;
    const int MIN_COUNT = 30; // Muestra mínima válida

    for (auto& pair : patterns) {
        auto& stat = pair.second;
        if (stat.count >= MIN_COUNT) {
            stat.mean_ret = stat.sum_ret / stat.count;
            double variance = (stat.sq_sum_ret - (stat.sum_ret * stat.sum_ret / stat.count)) / (stat.count - 1);
            
            if (variance > 0.0) {
                double std_err = std::sqrt(variance / stat.count);
                stat.t_stat = stat.mean_ret / std_err;
                stat.p_value = calculate_p_value(stat.t_stat);
                
                // Solo nos interesan patrones con retorno esperado positivo
                if (stat.t_stat > 0.0) {
                    evaluated.push_back(stat);
                }
            }
        }
    }

    // Ordenar por p-value ascendente (con desempate determinista por ID)
    std::sort(evaluated.begin(), evaluated.end(), [](const PatternStat& a, const PatternStat& b) {
        if (std::abs(a.p_value - b.p_value) < 1e-9) return a.pattern_id < b.pattern_id;
        return a.p_value < b.p_value;
    });

    // Implementación Benjamini-Hochberg (Step-Up)
    size_t m = evaluated.size();
    const double q_threshold = 0.05;
    size_t k = 0;

    for (size_t i = 0; i < m; ++i) {
        if (evaluated[i].p_value <= ((double)(i + 1) / m) * q_threshold) {
            k = i + 1;
        }
    }

    for (size_t i = 0; i < k; ++i) {
        evaluated[i].survives_fdr = true;
    }

    std::cout << "\n=== RESULTADOS MOTOR CANDLEFDR ===" << std::endl;
    std::cout << "Evaluados (count >= " << MIN_COUNT << " y t > 0): " << m << std::endl;
    std::cout << "Significativos (FDR Pass): " << k << std::endl;

    std::ofstream out_file("winners.csv");
    out_file << "pattern_id\n";

    for (const auto& stat : evaluated) {
        if (stat.survives_fdr) {
            std::cout << "-> PATRÓN GANADOR: " << stat.pattern_id 
                      << " | Mean Ret: " << stat.mean_ret * 100 << "%"
                      << " | t-stat: " << stat.t_stat 
                      << " | p-value: " << stat.p_value << std::endl;
            out_file << stat.pattern_id << "\n";
        }
    }
    out_file.close();

    return 0;
}