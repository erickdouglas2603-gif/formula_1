# OpenF1 API — Documentação Resumida

Fonte: https://openf1.org/docs/#api-endpoints

## Visão Geral

A OpenF1 é uma API open-source (não oficial, sem vínculo com a F1) que fornece dados de telemetria, timing e sessões da Fórmula 1.

- **Base URL**: `https://api.openf1.org/v1/`
- **Dados históricos (2023+)**: gratuitos, sem necessidade de autenticação.
- **Dados em tempo real**: exigem assinatura paga.

## Formato das Respostas

- **JSON**: formato padrão.
- **CSV**: adicione `csv=true` na query string para exportar como planilha.

## Filtros de Query

Aplicáveis a qualquer atributo (exceto campos do tipo array):

- Operadores de comparação: `>=`, `<=`, `>`, `<`, `=`
- Múltiplos valores no mesmo parâmetro: `parameter=value1&parameter=value2`
- Filtros por data: aceitam vários formatos (ex.: ISO 8601)

**Exemplo:**
```
https://api.openf1.org/v1/laps?session_key=9222&driver_number=55&is_pit_out_lap=true&lap_duration>=120
```

## Endpoints Principais

| Endpoint | Descrição | Principais parâmetros |
|---|---|---|
| `car_data` | Telemetria do carro (~3.7 Hz): velocidade, freio, acelerador, marcha, RPM, DRS | `driver_number`, `session_key`, `speed`, `brake`, `throttle`, `rpm` |
| `championship_drivers` (beta) | Classificação do campeonato de pilotos (apenas corridas) | `session_key`, `driver_number` |
| `championship_teams` (beta) | Classificação do campeonato de construtores | `session_key`, `team_name` |
| `drivers` | Informações dos pilotos em uma sessão (nome, equipe, número, foto) | `driver_number`, `session_key` |
| `intervals` | Intervalo em tempo real entre pilotos (apenas corridas, ~4s) | `session_key`, `interval`, `driver_number` |
| `laps` | Detalhes de voltas individuais (tempos por setor, velocidades) | `session_key`, `driver_number`, `lap_number` |
| `location` | Posição aproximada (x, y, z) dos carros na pista (~3.7 Hz) | `session_key`, `driver_number`, `date` |
| `meetings` | Informações sobre um Grande Prêmio / fim de semana de testes | `year`, `country_name`, `circuit_short_name` |
| `overtakes` | Ultrapassagens ocorridas (apenas corridas) | `session_key`, `overtaking_driver_number`, `overtaken_driver_number`, `position` |
| `pit` | Passagens pelo pit lane (duração do pit stop) | `session_key`, `driver_number`, `stop_duration`, `lane_duration` |
| `position` | Posição de cada piloto ao longo da sessão | `meeting_key`, `driver_number`, `position` |
| `race_control` | Eventos de controle de prova: bandeiras, safety car, incidentes | `flag`, `driver_number`, `date` |
| `sessions` | Informações de sessões individuais (treino, classificação, corrida) | `country_name`, `session_name`, `year` |
| `session_result` | Classificação final da sessão | `session_key`, `position` |
| `starting_grid` | Grid de largada da corrida | `session_key`, `position` |
| `stints` | Períodos contínuos com um mesmo pneu | `session_key`, `tyre_age_at_start` |
| `team_radio` | Gravações de rádio entre piloto e equipe (cobertura limitada) | `session_key`, `driver_number` |
| `weather` | Condições climáticas (atualizado a cada minuto) | `meeting_key`, `wind_direction`, `track_temperature` |

## Detalhes dos Endpoints

### car_data
Dados de telemetria por carro, a ~3.7 Hz.
**Campos**: `brake`, `date`, `driver_number`, `drs`, `meeting_key`, `n_gear`, `rpm`, `session_key`, `speed`, `throttle`

### championship_drivers (beta)
**Campos**: `driver_number`, `meeting_key`, `points_current`, `points_start`, `position_current`, `position_start`, `session_key`

### championship_teams (beta)
**Campos**: `meeting_key`, `points_current`, `points_start`, `position_current`, `position_start`, `session_key`, `team_name`

### drivers
**Campos**: `broadcast_name`, `driver_number`, `first_name`, `full_name`, `headshot_url`, `last_name`, `meeting_key`, `name_acronym`, `session_key`, `team_colour`, `team_name`

### intervals
**Campos**: `date`, `driver_number`, `gap_to_leader`, `interval`, `meeting_key`, `session_key`

### laps
**Campos**: `date_start`, `driver_number`, `duration_sector_1`, `duration_sector_2`, `duration_sector_3`, `i1_speed`, `i2_speed`, `is_pit_out_lap`, `lap_duration`, `lap_number`, `meeting_key`, `segments_sector_1`, `segments_sector_2`, `segments_sector_3`, `session_key`, `st_speed`

### location
**Campos**: `date`, `driver_number`, `meeting_key`, `session_key`, `x`, `y`, `z`

### meetings
**Campos**: `circuit_key`, `circuit_info_url`, `circuit_image`, `circuit_short_name`, `circuit_type`, `country_code`, `country_flag`, `country_key`, `country_name`, `date_end`, `date_start`, `gmt_offset`, `is_cancelled`, `location`, `meeting_key`, `meeting_name`, `meeting_official_name`, `year`

### overtakes
**Campos**: `date`, `meeting_key`, `overtaken_driver_number`, `overtaking_driver_number`, `position`, `session_key`

### pit
**Campos**: `date`, `driver_number`, `lane_duration`, `lap_number`, `meeting_key`, `pit_duration`, `session_key`, `stop_duration`

### position
**Campos**: `date`, `driver_number`, `meeting_key`, `position`, `session_key`

### race_control
**Campos**: `category`, `date`, `driver_number`, `flag`, `lap_number`, `meeting_key`, `message`, `qualifying_phase`, `scope`, `sector`, `session_key`

### sessions
**Campos**: `circuit_key`, `circuit_short_name`, `country_code`, `country_key`, `country_name`, `date_end`, `date_start`, `gmt_offset`, `is_cancelled`, `location`, `meeting_key`, `session_key`, `session_name`, `session_type`, `year`

### session_result
**Campos**: `dnf`, `dns`, `dsq`, `driver_number`, `duration`, `gap_to_leader`, `number_of_laps`, `meeting_key`, `position`, `session_key`

### starting_grid
**Campos**: `position`, `driver_number`, `lap_duration`, `meeting_key`, `session_key`

### stints
**Campos**: `compound`, `driver_number`, `lap_end`, `lap_start`, `meeting_key`, `session_key`, `stint_number`, `tyre_age_at_start`

### team_radio
**Campos**: `date`, `driver_number`, `meeting_key`, `recording_url`, `session_key`

### weather
**Campos**: `air_temperature`, `date`, `humidity`, `meeting_key`, `pressure`, `rainfall`, `session_key`, `track_temperature`, `wind_direction`, `wind_speed`

## Chaves de Referência

- `session_key`: identifica uma sessão específica (treino, classificação, corrida).
- `meeting_key`: identifica um fim de semana de Grande Prêmio inteiro.
- `driver_number`: número do piloto (ex.: 1, 44, 55).

## Exemplo de Uso (Python)

```python
import requests

response = requests.get(
    "https://api.openf1.org/v1/laps", params={"session_key": 9222, "driver_number": 55}
)
data = response.json()
```
