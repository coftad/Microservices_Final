@echo off
echo ========================================
echo Microservices Load Testing Suite
echo ========================================

REM Test 1: Light Load (10 users)
echo.
echo Test 1: Light Load (10 concurrent users)
locust -f locustfile.py --headless --users 10 --spawn-rate 2 --run-time 2m --html reports/light_load_report.html --csv reports/light_load

timeout /t 10

REM Test 2: Medium Load (20 users)
echo.
echo Test 1: Light Load (20 concurrent users)
locust -f locustfile.py --headless --users 10 --spawn-rate 3 --run-time 2m --html reports/medium_load_report.html --csv reports/medium_load

timeout /t 10

REM Test 3: High Load (50 users)
echo.
echo Test 2: High Load (50 concurrent users)
locust -f locustfile.py --headless --users 50 --spawn-rate 5 --run-time 3m --html reports/high_load_report.html --csv reports/high_load


echo.
echo ========================================
echo All tests completed!
echo Reports saved in ./reports/
echo ========================================
pause