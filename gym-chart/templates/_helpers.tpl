{{/*
Generate the chart name.
*/}}
{{- define "gym.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Generate the fully qualified resource name.
*/}}
{{- define "gym.fullname" -}}
{{- if .Values.fullnameOverride -}}
  {{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
  {{- printf "%s-%s" .Release.Name (include "gym.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
