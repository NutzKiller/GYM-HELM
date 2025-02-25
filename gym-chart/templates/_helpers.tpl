{{- define "gym.name" -}}
gym
{{- end -}}

{{- define "gym.fullname" -}}
{{ .Release.Name }}-gym
{{- end -}}
