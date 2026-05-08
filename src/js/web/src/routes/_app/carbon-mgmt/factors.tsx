/**
 * 排放因子库 - 列表/简单筛选
 * API: /api/carbon/emission-factors
 */
import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useMemo, useState } from "react"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { PageContainer, PageHeader, PageSection } from "@/components/ui/page-layout"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

type EmissionFactor = {
  id: number
  scope: string
  category: string
  sub_category: string
  unit: string
  factor_value: string | number
  factor_unit: string
  year: number
  source: string
  is_active: boolean
}

type ApiResponse<T> = { code: number; msg: string; data: T }

export const Route = createFileRoute("/_app/carbon-mgmt/factors")({
  component: FactorsPage,
})

function FactorsPage() {
  const [scope, setScope] = useState<string>("all")
  const [keyword, setKeyword] = useState("")
  const { data, isLoading, isError } = useQuery<ApiResponse<EmissionFactor[]>>({
    queryKey: ["carbon-mgmt", "factors"],
    queryFn: async () => {
      const res = await fetch("/api/carbon/emission-factors")
      return res.json()
    },
  })

  const items = useMemo(() => {
    const raw = data?.data ?? []
    const kw = keyword.trim().toLowerCase()
    return raw.filter((f) => {
      const okScope = scope === "all" ? true : f.scope === scope
      const hay = `${f.category ?? ""} ${f.sub_category ?? ""} ${f.source ?? ""}`.toLowerCase()
      const okKw = kw.length === 0 ? true : hay.includes(kw)
      return okScope && okKw
    })
  }, [data?.data, keyword, scope])

  return (
    <PageContainer className="flex-1 space-y-6">
      <PageHeader eyebrow="碳排放管理" title="排放因子库" description="用于碳排放计算的排放因子列表，仅支持查看与筛选。" />

      <PageSection>
        <Card>
          <CardHeader className="space-y-3">
            <CardTitle>因子列表</CardTitle>
            <div className="flex flex-wrap items-center gap-3">
              <div className="w-[140px]">
                <Select value={scope} onValueChange={setScope}>
                  <SelectTrigger>
                    <SelectValue placeholder="范围" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">全部范围</SelectItem>
                    <SelectItem value="Scope1">Scope1</SelectItem>
                    <SelectItem value="Scope2">Scope2</SelectItem>
                    <SelectItem value="Scope3">Scope3</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="min-w-[260px] flex-1">
                <Input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="搜索：类别/子类/来源…" />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading && <div className="text-sm text-muted-foreground">正在加载…</div>}
            {isError && <div className="text-sm text-destructive">加载失败，请检查后端接口。</div>}
            {!isLoading && !isError && (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>范围</TableHead>
                    <TableHead>类别</TableHead>
                    <TableHead>子类</TableHead>
                    <TableHead>活动量单位</TableHead>
                    <TableHead className="text-right">因子数值</TableHead>
                    <TableHead>因子单位</TableHead>
                    <TableHead>年份</TableHead>
                    <TableHead>来源</TableHead>
                    <TableHead>状态</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={9} className="h-24 text-center text-muted-foreground">
                        暂无数据
                      </TableCell>
                    </TableRow>
                  )}
                  {items.map((f) => (
                    <TableRow key={f.id}>
                      <TableCell>{f.scope}</TableCell>
                      <TableCell>{f.category}</TableCell>
                      <TableCell>{f.sub_category}</TableCell>
                      <TableCell>{f.unit}</TableCell>
                      <TableCell className="text-right">{String(f.factor_value)}</TableCell>
                      <TableCell>{f.factor_unit}</TableCell>
                      <TableCell>{f.year}</TableCell>
                      <TableCell>{f.source}</TableCell>
                      <TableCell>{f.is_active ? <Badge>启用</Badge> : <Badge variant="outline">停用</Badge>}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </PageSection>
    </PageContainer>
  )
}

