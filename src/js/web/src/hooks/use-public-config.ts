import { useQuery } from "@tanstack/react-query"

export interface PublicAppConfig {
  displayName: string
  shortName: string
  description: string
}

export const defaultPublicConfig: PublicAppConfig = {
  displayName: "碳数据收集与管理系统",
  shortName: "CD",
  description: "支持 Scope 1/2/3 碳排放数据的采集、审核与统计分析。",
}

async function fetchPublicConfig(): Promise<PublicAppConfig> {
  const apiUrl = import.meta.env.VITE_API_URL ?? ""
  const response = await fetch(`${apiUrl}/api/config/public`)

  if (!response.ok) {
    return defaultPublicConfig
  }

  return { ...defaultPublicConfig, ...(await response.json()) }
}

export function usePublicConfig() {
  const query = useQuery({
    queryKey: ["public-config"],
    queryFn: fetchPublicConfig,
    staleTime: 1000 * 60 * 5,
    retry: false,
  })

  return {
    ...query,
    config: query.data ?? defaultPublicConfig,
  }
}
