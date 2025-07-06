#!/usr/bin/env python3
"""
Comprehensive profiling script for the NLP Parser
Measures CPU time, memory usage, and performance metrics
"""

import cProfile
import pstats
import time
import tracemalloc
import psutil
import os
import sys
from memory_profiler import memory_usage
from parser import LightweightNLPParser

class PerformanceProfiler:
    def __init__(self):
        self.parser = None
        self.results = {}
        
    def setup_parser(self):
        """Initialize the parser"""
        print("🚀 Setting up parser...")
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        self.parser = LightweightNLPParser(use_spacy=True, model_size="small")
        self.parser.load_models()
        
        setup_time = time.time() - start_time
        setup_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        self.results['setup'] = {
            'time': setup_time,
            'memory_before': start_memory,
            'memory_after': setup_memory,
            'memory_increase': setup_memory - start_memory
        }
        
        print(f"✅ Parser setup complete in {setup_time:.2f}s")
        print(f"📊 Memory: {start_memory:.1f}MB → {setup_memory:.1f}MB "
              f"(+{setup_memory - start_memory:.1f}MB)")
        
    def profile_single_command(self, command: str, description: str = ""):
        """Profile a single command parsing"""
        print(f"\n🔍 Profiling: '{command}' {description}")
        
        # Warmup run
        self.parser.parse(command)
        
        # Measure memory usage during parsing
        def parse_command():
            return self.parser.parse(command)
        
        start_time = time.time()
        mem_usage = memory_usage(parse_command, interval=0.01, timeout=10)
        end_time = time.time()
        
        # Multiple runs for timing accuracy
        runs = 100
        total_time = 0
        
        for _ in range(runs):
            start = time.perf_counter()
            result = self.parser.parse(command)
            end = time.perf_counter()
            total_time += (end - start)
        
        avg_time = total_time / runs
        
        profile_result = {
            'command': command,
            'description': description,
            'avg_time_ms': avg_time * 1000,
            'memory_peak_mb': max(mem_usage) if mem_usage else 0,
            'memory_baseline_mb': min(mem_usage) if mem_usage else 0,
            'result': {
                'verbs': result.verbs,
                'direct_object': result.direct_object,
                'indirect_object': result.indirect_object,
                'prepositions': result.prepositions,
                'entities': len(result.entities)
            }
        }
        
        print(f"⏱️  Average time: {avg_time * 1000:.2f}ms")
        print(f"🧠 Memory peak: {max(mem_usage) if mem_usage else 0:.1f}MB")
        print(f"📈 Result: {len(result.verbs)} verbs, "
              f"{1 if result.direct_object else 0} direct obj, "
              f"{len(result.prepositions)} prepositions")
        
        return profile_result
        
    def profile_cprofile(self, commands):
        """Detailed CPU profiling with cProfile"""
        print("\n🔬 Running detailed CPU profiling...")
        
        def run_parsing_batch():
            for cmd, _ in commands:
                self.parser.parse(cmd)
        
        # Run with cProfile
        profiler = cProfile.Profile()
        profiler.enable()
        
        # Run parsing multiple times
        for _ in range(10):
            run_parsing_batch()
            
        profiler.disable()
        
        # Save profile stats
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        
        # Save to file
        import io
        import contextlib
        
        with open('profile_stats.txt', 'w') as f:
            f.write("CPU PROFILING RESULTS\n")
            f.write("=" * 50 + "\n\n")
            
            # Capture print_stats output
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                stats.print_stats(20)
            f.write(output.getvalue())
            
        print("📄 Detailed CPU profile saved to 'profile_stats.txt'")
        
        # Get basic stats summary
        return {
            'total_calls': stats.total_calls,
            'total_time': stats.total_tt,
            'profile_saved': True
        }
    
    def benchmark_test_suite(self):
        """Profile the entire test suite"""
        print("\n🧪 Profiling test suite execution...")
        
        import subprocess
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Run tests with timing
        result = subprocess.run([
            'python', '-m', 'pytest', 'tests/test_parser_steps.py', '-v', '--tb=short'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        test_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        # Parse test results
        output_lines = result.stdout.split('\n')
        passed_tests = len([line for line in output_lines if 'PASSED' in line])
        failed_tests = len([line for line in output_lines if 'FAILED' in line])
        
        self.results['test_suite'] = {
            'total_time': test_time,
            'memory_increase': memory_used,
            'tests_passed': passed_tests,
            'tests_failed': failed_tests,
            'return_code': result.returncode
        }
        
        print(f"⏱️  Test suite completed in {test_time:.2f}s")
        print(f"📊 Memory change: {memory_used:+.1f}MB")
        print(f"✅ Tests: {passed_tests} passed, {failed_tests} failed")
        
        return self.results['test_suite']
    
    def generate_report(self):
        """Generate comprehensive performance report"""
        print("\n📋 Generating Performance Report...")
        
        report = []
        report.append("# NLP Parser Performance Report")
        report.append("=" * 50)
        report.append("")
        
        # System info
        process = psutil.Process()
        report.append("## System Information")
        report.append(f"- Python version: {sys.version.split()[0]}")
        report.append(f"- Platform: {sys.platform}")
        report.append(f"- CPU cores: {psutil.cpu_count()}")
        report.append(f"- Available memory: {psutil.virtual_memory().total / 1024**3:.1f}GB")
        report.append("")
        
        # Setup performance
        if 'setup' in self.results:
            setup = self.results['setup']
            report.append("## Parser Initialization")
            report.append(f"- Setup time: {setup['time']:.2f}s")
            report.append(f"- Memory increase: {setup['memory_increase']:.1f}MB")
            report.append(f"- Final memory usage: {setup['memory_after']:.1f}MB")
            report.append("")
        
        # Command benchmarks
        if 'commands' in self.results:
            report.append("## Command Parsing Performance")
            report.append("| Command | Time (ms) | Memory (MB) | Result |")
            report.append("|---------|-----------|-------------|---------|")
            
            for cmd_result in self.results['commands']:
                cmd = cmd_result['command'][:30] + "..." if len(cmd_result['command']) > 30 else cmd_result['command']
                time_ms = cmd_result['avg_time_ms']
                memory = cmd_result['memory_peak_mb']
                result_summary = f"{len(cmd_result['result']['verbs'])}v, {1 if cmd_result['result']['direct_object'] else 0}o"
                
                report.append(f"| {cmd} | {time_ms:.2f} | {memory:.1f} | {result_summary} |")
            report.append("")
        
        # Test suite performance
        if 'test_suite' in self.results:
            test = self.results['test_suite']
            report.append("## Test Suite Performance")
            report.append(f"- Total execution time: {test['total_time']:.2f}s")
            report.append(f"- Memory usage change: {test['memory_increase']:+.1f}MB")
            report.append(f"- Tests passed: {test['tests_passed']}")
            report.append(f"- Tests failed: {test['tests_failed']}")
            report.append("")
        
        # Performance summary
        if 'commands' in self.results and self.results['commands']:
            times = [cmd['avg_time_ms'] for cmd in self.results['commands']]
            memories = [cmd['memory_peak_mb'] for cmd in self.results['commands']]
            
            report.append("## Performance Summary")
            report.append(f"- Average parsing time: {sum(times)/len(times):.2f}ms")
            report.append(f"- Fastest parsing: {min(times):.2f}ms")
            report.append(f"- Slowest parsing: {max(times):.2f}ms")
            report.append(f"- Average memory usage: {sum(memories)/len(memories):.1f}MB")
            report.append("")
        
        report_text = "\n".join(report)
        
        # Save report
        with open('performance_report.md', 'w') as f:
            f.write(report_text)
        
        print("📄 Performance report saved to 'performance_report.md'")
        return report_text

def main():
    profiler = PerformanceProfiler()
    
    # Test commands for benchmarking
    test_commands = [
        ("take the sword", "Simple command"),
        ("take the ball and kick it at the window", "Pronoun resolution"),
        ("I want to look at the ball", "Conversational wrapper"),
        ("talk to John about the quest", "Entity recognition"),
        ("put the book on the table", "Multiple objects"),
        ("examine the scroll and read that", "Demonstrative pronoun"),
        ("go north and then east and then look around", "Complex compound"),
        ("pick up the red key and unlock the heavy wooden door with it", "Long complex command")
    ]
    
    try:
        # Setup parser
        profiler.setup_parser()
        
        # Profile individual commands
        command_results = []
        for command, description in test_commands:
            result = profiler.profile_single_command(command, description)
            command_results.append(result)
        
        profiler.results['commands'] = command_results
        
        # CPU profiling
        cpu_profile = profiler.profile_cprofile(test_commands)
        profiler.results['cpu_profile'] = cpu_profile
        
        # Test suite profiling
        test_results = profiler.benchmark_test_suite()
        
        # Generate report
        report = profiler.generate_report()
        
        print("\n🎉 Profiling complete!")
        print("📁 Generated files:")
        print("  - performance_report.md")
        print("  - profile_stats.txt")
        
    except Exception as e:
        print(f"❌ Error during profiling: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()