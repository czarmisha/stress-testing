#!/bin/bash

# Количество запросов и параллельных потоков
total_requests=1000
parallel_requests=300
url="https://bringo.uz/"

# Массив для хранения времен выполнения
durations=()

# Функция для выполнения запроса
make_request() {
  start=$(date +%s%N)
  http_code=$(curl -s -o /dev/null -w "%{http_code}" --location "$url")
  end=$(date +%s%N)
  duration=$((end - start))
  duration_ms=$((duration / 1000000))
  echo "HTTP Code: $http_code, Duration: ${duration_ms}ms"
  echo $duration_ms >> durations.txt
}

# Удаляем файл, если он существует
rm -f durations.txt

# Выполняем запросы параллельно
for i in $(seq 1 $total_requests); do
  make_request &
  if (( $i % $parallel_requests == 0 )); then
    wait
  fi
done
wait

# Заполняем массив durations из файла
mapfile -t durations < durations.txt

# Вычисляем минимальное, максимальное и среднее время выполнения
min_duration=$(printf "%s\n" "${durations[@]}" | sort -n | head -n 1)
max_duration=$(printf "%s\n" "${durations[@]}" | sort -n | tail -n 1)
sum_duration=0

for duration in "${durations[@]}"; do
  sum_duration=$((sum_duration + duration))
done

avg_duration=$((sum_duration / $total_requests))

echo "Min Duration: $min_duration ms"
echo "Max Duration: $max_duration ms"
echo "Avg Duration: $avg_duration ms"
