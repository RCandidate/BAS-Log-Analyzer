# BAS Log Analyzer 🐧

**EN:**
A Python script to analyze logs from BrowserAutomationStudio (BAS). It parses `log.txt` to find thread executions that finished successfully, reconstructs the event history for those threads, and calculates the execution duration based on the "Setting up proxy" marker.

**RU:**
Python скрипт для анализа логов BrowserAutomationStudio (BAS). Скрипт ищет в файле `log.txt` успешные завершения потоков, восстанавливает хронологию событий для них и считает время выполнения, отсчитывая его от момента подключения прокси ("Setting up proxy").

## Features / Возможности
- 🔍 Finds successful thread completions backwards (tail-to-head parsing).
- 🕒 Calculates precise duration from "Setting up proxy" to success.
- 🎨 Colorized output for Linux terminal.
- 🧹 Cleans log IDs for better readability.
- 🚫 Ignores threads that crashed.

## Usage / Использование
1. Place `analyzer.py` in the folder with your `log.txt`.
2. Run:
   python3 analyzer.py
3.   View the colored report in the console!