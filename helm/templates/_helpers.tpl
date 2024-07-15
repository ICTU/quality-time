{{/* Returns the name of the api_server component service */}}
{{/* Abbreviated to "api", because this string may not contain underscores */}}
{{- define "api_server_name" -}}
api
{{- end -}}

{{/* Returns the name of the collector component service */}}
{{- define "collector_name" -}}
collector
{{- end -}}

{{/* Returns the name of the database component service */}}
{{- define "database_name" -}}
database
{{- end -}}

{{/* Returns the name of the frontend component service */}}
{{- define "frontend_name" -}}
frontend
{{- end -}}

{{/* Returns the name of the notifier component service */}}
{{- define "notifier_name" -}}
notifier
{{- end -}}

{{/* Returns the name of the renderer component service */}}
{{- define "renderer_name" -}}
renderer
{{- end -}}

{{/* Returns the name of the www service running the proxy component */}}
{{- define "www_name" -}}
www
{{- end -}}
