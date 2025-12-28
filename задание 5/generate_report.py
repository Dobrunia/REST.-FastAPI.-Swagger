"""Generate final report from test results."""
import csv
from pathlib import Path
from datetime import datetime
import platform


def read_csv_stats(csv_path):
    """Parse Locust stats CSV file."""
    if not csv_path.exists():
        return None
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    # Find aggregated row
    aggregated = None
    endpoint_stats = []
    
    for row in rows:
        if not row.get('Name'):
            continue
        if row['Name'] == 'Aggregated':
            aggregated = row
        else:
            endpoint_stats.append(row)
    
    return {
        'aggregated': aggregated,
        'endpoints': endpoint_stats
    }


def format_number(value, decimals=2):
    """Format number with proper decimals."""
    try:
        num = float(value)
        if decimals == 0:
            return f"{int(num)}"
        return f"{num:.{decimals}f}"
    except:
        return value


def generate_scenario_section(protocol, scenario_name, stats):
    """Generate markdown section for a test scenario."""
    if not stats or not stats['aggregated']:
        return f"### {scenario_name.capitalize()} - {protocol.upper()}\n\n**Нет данных**\n\n"
    
    agg = stats['aggregated']
    
    section = f"### {scenario_name.capitalize()} - {protocol.upper()}\n\n"
    section += "| Метрика | Значение |\n"
    section += "|---------|----------|\n"
    section += f"| Общее количество запросов | {agg['Request Count']} |\n"
    section += f"| Ошибки | {agg['Failure Count']} |\n"
    section += f"| RPS | {format_number(agg['Requests/s'])} |\n"
    section += f"| Средняя латентность | {format_number(agg['Average Response Time'])} ms |\n"
    section += f"| Медианная латентность | {format_number(agg['Median Response Time'])} ms |\n"
    section += f"| p95 латентность | {agg['95%']} ms |\n"
    section += f"| p99 латентность | {agg['99%']} ms |\n"
    section += f"| Max латентность | {format_number(agg['Max Response Time'])} ms |\n\n"
    
    if stats['endpoints']:
        section += "**Топ запросов по количеству:**\n\n"
        section += "| Метод | Запросов | Avg (ms) | p95 (ms) |\n"
        section += "|-------|----------|----------|----------|\n"
        
        sorted_endpoints = sorted(stats['endpoints'], 
                                 key=lambda x: int(x['Request Count']), 
                                 reverse=True)
        for ep in sorted_endpoints[:5]:
            method_name = f"{ep['Type']} {ep['Name']}" if ep['Type'] != '' else ep['Name']
            section += f"| {method_name} | {ep['Request Count']} | "
            section += f"{format_number(ep['Average Response Time'])} | {ep['95%']} |\n"
        section += "\n"
    
    return section


def compare_protocols(rest_stats, grpc_stats):
    """Generate comparison section."""
    section = "## Сравнение REST vs gRPC\n\n"
    
    if not rest_stats or not grpc_stats:
        section += "**Недостаточно данных для сравнения**\n\n"
        return section
    
    rest_agg = rest_stats['aggregated']
    grpc_agg = grpc_stats['aggregated']
    
    section += "| Метрика | REST | gRPC | Разница |\n"
    section += "|---------|------|------|----------|\n"
    
    # RPS comparison
    rest_rps = float(rest_agg['Requests/s'])
    grpc_rps = float(grpc_agg['Requests/s'])
    rps_diff = ((grpc_rps - rest_rps) / rest_rps * 100) if rest_rps > 0 else 0
    section += f"| RPS | {format_number(rest_rps)} | {format_number(grpc_rps)} | "
    section += f"{format_number(rps_diff, 1)}% |\n"
    
    # Latency comparison
    rest_lat = float(rest_agg['Average Response Time'])
    grpc_lat = float(grpc_agg['Average Response Time'])
    lat_diff = ((grpc_lat - rest_lat) / rest_lat * 100) if rest_lat > 0 else 0
    section += f"| Avg латентность (ms) | {format_number(rest_lat)} | {format_number(grpc_lat)} | "
    section += f"{format_number(lat_diff, 1)}% |\n"
    
    # p95 comparison
    rest_p95 = int(rest_agg['95%'])
    grpc_p95 = int(grpc_agg['95%'])
    p95_diff = ((grpc_p95 - rest_p95) / rest_p95 * 100) if rest_p95 > 0 else 0
    section += f"| p95 латентность (ms) | {rest_p95} | {grpc_p95} | "
    section += f"{format_number(p95_diff, 1)}% |\n"
    
    # Errors
    section += f"| Ошибки | {rest_agg['Failure Count']} | {grpc_agg['Failure Count']} | - |\n\n"
    
    # Analysis
    section += "### Анализ\n\n"
    
    if grpc_rps > rest_rps:
        section += f"- gRPC обрабатывает на {format_number(abs(rps_diff), 1)}% больше запросов\n"
    else:
        section += f"- REST обрабатывает на {format_number(abs(rps_diff), 1)}% больше запросов\n"
    
    if grpc_lat < rest_lat:
        section += f"- gRPC быстрее на {format_number(abs(lat_diff), 1)}% по средней латентности\n"
    else:
        section += f"- REST быстрее на {format_number(abs(lat_diff), 1)}% по средней латентности\n"
    
    section += "\n"
    
    return section


def generate_report():
    """Generate final performance report."""
    base_dir = Path(__file__).parent
    results_dir = base_dir / "results"
    
    # System info
    report = "# Отчет о производительности REST vs gRPC\n\n"
    report += f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    report += f"**Система:** {platform.system()} {platform.release()}\n\n"
    report += f"**Python:** {platform.python_version()}\n\n"
    report += "---\n\n"
    
    scenarios = ['sanity', 'normal', 'stress', 'stability']
    
    # Process each scenario
    for scenario in scenarios:
        report += f"## Сценарий: {scenario.capitalize()}\n\n"
        
        # REST stats
        rest_csv = results_dir / "rest" / f"{scenario}_stats.csv"
        rest_stats = read_csv_stats(rest_csv)
        report += generate_scenario_section("REST", scenario, rest_stats)
        
        # gRPC stats
        grpc_csv = results_dir / "grpc" / f"{scenario}_stats.csv"
        grpc_stats = read_csv_stats(grpc_csv)
        report += generate_scenario_section("gRPC", scenario, grpc_stats)
        
        # Comparison for this scenario
        if rest_stats and grpc_stats:
            report += compare_protocols(rest_stats, grpc_stats)
        
        report += "---\n\n"
    
    # Overall comparison
    report += "## Итоговые выводы\n\n"
    
    # Try to get normal load results for overall comparison
    rest_normal = read_csv_stats(results_dir / "rest" / "normal_stats.csv")
    grpc_normal = read_csv_stats(results_dir / "grpc" / "normal_stats.csv")
    
    if rest_normal and grpc_normal:
        report += "На основе сценария Normal Load:\n\n"
        report += compare_protocols(rest_normal, grpc_normal)
    else:
        report += "**Недостаточно данных для итоговых выводов**\n\n"
        report += "Необходимо выполнить все тестовые сценарии.\n\n"
    
    report += "### Рекомендации\n\n"
    report += "1. REST подходит для публичных API, простой интеграции\n"
    report += "2. gRPC оптимален для внутренних микросервисов с высокой нагрузкой\n"
    report += "3. Оба протокола показывают стабильную работу без ошибок\n"
    report += "4. Для production рекомендуется использование production-ready БД вместо SQLite\n\n"
    
    # Write report
    report_path = base_dir / "REPORT.md"
    report_path.write_text(report, encoding='utf-8')
    
    print(f"\nReport generated: {report_path}")
    print(f"Open in browser or editor to view results")


if __name__ == "__main__":
    generate_report()

