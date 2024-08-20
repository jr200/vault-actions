{{/*
Expand the name of the chart.
*/}}
{{- define "vault-actions.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "vault-actions.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "vault-actions.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "vault-actions.labels" -}}
helm.sh/chart: {{ include "vault-actions.chart" . }}
{{ include "vault-actions.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "vault-actions.selectorLabels" -}}
app.kubernetes.io/name: {{ include "vault-actions.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "vault-actions.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "vault-actions.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Get secret name for configuration
*/}}
{{- define "vault-actions.secretName" -}}
{{- default (include "vault-actions.fullname" . | trunc 63 | trimSuffix "-") ( tpl .Values.secretName . ) }}
{{- end }}

{{/*
Get mount path for configuration
*/}}
{{- define "vault-actions.secretMountPath" -}}
{{- default "/config/vault-actions.yaml" .Values.secretPathOverride }}
{{- end }}

