/**
 * [Scope2] 电费账单 - 列表/新增/送审/通过/驳回/删除
 * API: /api/carbon/scope2-electricity-bill
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useMemo, useState } from "react"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { PageContainer, PageHeader, PageSection } from "@/components/ui/page-layout"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Textarea } from "@/components/ui/textarea"

type Scope2Bill = {
  id: number
  account_number: string
  billing_month: string
  total_kwh: string | number
  peak_kwh?: string | number | null
  flat_kwh?: string | number | null
  valley_kwh?: string | number | null
  amount_cny?: string | number | null
  attachment?: string | null
  remark?: string | null
  status?: string
  approved_at?: string | null
  reject_reason?: string | null
}

type ApiResponse<T> = { code: number; msg: string; data: T }

export const Route = createFileRoute("/_app/carbon-mgmt/scope2-bill")({
  component: Scope2BillPage,
})

function Scope2BillPage() {
  const qc = useQueryClient()
  const [keyword, setKeyword] = useState("")
  const [status, setStatus] = useState<string>("all")
  const [createOpen, setCreateOpen] = useState(false)

  const [form, setForm] = useState({
    account_number: "",
    billing_month: "",
    total_kwh: "",
    peak_kwh: "",
    flat_kwh: "",
    valley_kwh: "",
    amount_cny: "",
    remark: "",
  })

  const listQuery = useQuery<ApiResponse<Scope2Bill[]>>({
    queryKey: ["carbon-mgmt", "scope2-bill", "list"],
    queryFn: async () => {
      const res = await fetch("/api/carbon/scope2-electricity-bill")
      return res.json()
    },
  })

  const items = useMemo(() => {
    const raw = listQuery.data?.data ?? []
    const kw = keyword.trim().toLowerCase()
    return raw.filter((r) => {
      const okStatus = status === "all" ? true : (r.status ?? "draft") === status
      const hay = `${r.account_number ?? ""} ${r.billing_month ?? ""}`.toLowerCase()
      const okKw = kw.length === 0 ? true : hay.includes(kw)
      return okStatus && okKw
    })
  }, [keyword, listQuery.data?.data, status])

  const createMut = useMutation({
    mutationFn: async () => {
      const payload = {
        account_number: form.account_number,
        billing_month: form.billing_month,
        total_kwh: form.total_kwh,
        peak_kwh: String(form.peak_kwh).trim() ? form.peak_kwh : null,
        flat_kwh: String(form.flat_kwh).trim() ? form.flat_kwh : null,
        valley_kwh: String(form.valley_kwh).trim() ? form.valley_kwh : null,
        amount_cny: String(form.amount_cny).trim() ? form.amount_cny : null,
        remark: form.remark || null,
      }
      const res = await fetch("/api/carbon/scope2-electricity-bill", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload),
      })
      const json = (await res.json()) as ApiResponse<Scope2Bill>
      if (!res.ok) throw new Error(json.msg || "新增失败")
      return json.data
    },
    onSuccess: async () => {
      toast.success("新增成功")
      setCreateOpen(false)
      setForm({
        account_number: "",
        billing_month: "",
        total_kwh: "",
        peak_kwh: "",
        flat_kwh: "",
        valley_kwh: "",
        amount_cny: "",
        remark: "",
      })
      await qc.invalidateQueries({ queryKey: ["carbon-mgmt", "scope2-bill", "list"] })
    },
    onError: (e) => toast.error("新增失败", { description: e instanceof Error ? e.message : "请稍后重试" }),
  })

  const actionMut = useMutation({
    mutationFn: async (args: { id: number; action: "submit" | "approve" | "reject" | "delete" }) => {
      const { id, action } = args
      if (action === "delete") {
        const res = await fetch(`/api/carbon/scope2-electricity-bill/${id}`, { method: "DELETE" })
        const json = (await res.json()) as ApiResponse<unknown>
        if (!res.ok) throw new Error(json.msg || "删除失败")
        return
      }
      const res = await fetch(`/api/carbon/scope2-electricity-bill/${id}/${action}`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: action === "reject" ? JSON.stringify({ reason: "不符合审核要求" }) : undefined,
      })
      const json = (await res.json()) as ApiResponse<unknown>
      if (!res.ok) throw new Error(json.msg || "操作失败")
    },
    onSuccess: async () => {
      toast.success("操作成功")
      await qc.invalidateQueries({ queryKey: ["carbon-mgmt", "scope2-bill", "list"] })
    },
    onError: (e) => toast.error("操作失败", { description: e instanceof Error ? e.message : "请稍后重试" }),
  })

  function statusBadge(st?: string) {
    if (st === "approved") return <Badge>已通过</Badge>
    if (st === "pending") return <Badge variant="secondary">待审核</Badge>
    if (st === "rejected") return <Badge variant="destructive">已驳回</Badge>
    return <Badge variant="outline">草稿</Badge>
  }

  return (
    <PageContainer className="flex-1 space-y-6">
      <PageHeader eyebrow="碳排放管理" title="[范围2] 电费账单" description="电费账单填报、审核流转与记录管理。" />

      <PageSection>
        <Card>
          <CardHeader className="space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <CardTitle>数据列表</CardTitle>
              <div className="flex flex-wrap gap-2">
                <Dialog open={createOpen} onOpenChange={setCreateOpen}>
                  <DialogTrigger asChild>
                    <Button>新增</Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>新增 - 电费账单</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4">
                      <div className="grid gap-2">
                        <Label>户号</Label>
                        <Input value={form.account_number} onChange={(e) => setForm((s) => ({ ...s, account_number: e.target.value }))} placeholder="例如：电力户号/表号" />
                      </div>
                      <div className="grid gap-2">
                        <Label>账期（月）</Label>
                        <Input value={form.billing_month} onChange={(e) => setForm((s) => ({ ...s, billing_month: e.target.value }))} placeholder="例如：2026-03" />
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="grid gap-2">
                          <Label>总电量(kWh)</Label>
                          <Input value={form.total_kwh} onChange={(e) => setForm((s) => ({ ...s, total_kwh: e.target.value }))} placeholder="例如：1234.5" />
                        </div>
                        <div className="grid gap-2">
                          <Label>金额(元)</Label>
                          <Input value={form.amount_cny} onChange={(e) => setForm((s) => ({ ...s, amount_cny: e.target.value }))} placeholder="可选" />
                        </div>
                      </div>
                      <div className="grid grid-cols-3 gap-3">
                        <div className="grid gap-2">
                          <Label>峰(kWh)</Label>
                          <Input value={form.peak_kwh} onChange={(e) => setForm((s) => ({ ...s, peak_kwh: e.target.value }))} placeholder="可选" />
                        </div>
                        <div className="grid gap-2">
                          <Label>平(kWh)</Label>
                          <Input value={form.flat_kwh} onChange={(e) => setForm((s) => ({ ...s, flat_kwh: e.target.value }))} placeholder="可选" />
                        </div>
                        <div className="grid gap-2">
                          <Label>谷(kWh)</Label>
                          <Input value={form.valley_kwh} onChange={(e) => setForm((s) => ({ ...s, valley_kwh: e.target.value }))} placeholder="可选" />
                        </div>
                      </div>
                      <div className="grid gap-2">
                        <Label>备注</Label>
                        <Textarea value={form.remark} onChange={(e) => setForm((s) => ({ ...s, remark: e.target.value }))} placeholder="可选" />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setCreateOpen(false)}>
                        取消
                      </Button>
                      <Button
                        onClick={() => createMut.mutate()}
                        disabled={!form.account_number.trim() || !form.billing_month.trim() || !String(form.total_kwh).trim() || createMut.isPending}
                      >
                        保存
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
                <Button variant="outline" onClick={() => (setKeyword(""), setStatus("all"))}>
                  重置
                </Button>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <div className="min-w-[260px] flex-1">
                <Input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="搜索：户号/账期…" />
              </div>
              <div className="w-[160px]">
                <Select value={status} onValueChange={setStatus}>
                  <SelectTrigger>
                    <SelectValue placeholder="状态" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">全部状态</SelectItem>
                    <SelectItem value="draft">草稿</SelectItem>
                    <SelectItem value="pending">待审核</SelectItem>
                    <SelectItem value="approved">已通过</SelectItem>
                    <SelectItem value="rejected">已驳回</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button variant="secondary" onClick={() => listQuery.refetch()} disabled={listQuery.isFetching}>
                查询
              </Button>
            </div>
          </CardHeader>

          <CardContent className="space-y-3">
            {listQuery.isLoading && <div className="text-sm text-muted-foreground">正在加载…</div>}
            {listQuery.isError && <div className="text-sm text-destructive">加载失败，请检查后端接口。</div>}

            {!listQuery.isLoading && !listQuery.isError && (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>户号</TableHead>
                    <TableHead>账期</TableHead>
                    <TableHead className="text-right">总电量(kWh)</TableHead>
                    <TableHead className="text-right">金额(元)</TableHead>
                    <TableHead>状态</TableHead>
                    <TableHead className="text-right">操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={6} className="h-24 text-center text-muted-foreground">
                        暂无数据
                      </TableCell>
                    </TableRow>
                  )}
                  {items.map((r) => {
                    const st = r.status ?? "draft"
                    return (
                      <TableRow key={r.id}>
                        <TableCell>{r.account_number}</TableCell>
                        <TableCell>{r.billing_month}</TableCell>
                        <TableCell className="text-right">{String(r.total_kwh)}</TableCell>
                        <TableCell className="text-right">{r.amount_cny === null || r.amount_cny === undefined ? "-" : String(r.amount_cny)}</TableCell>
                        <TableCell>{statusBadge(st)}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex flex-wrap justify-end gap-2">
                            <Button variant="outline" size="sm" onClick={() => actionMut.mutate({ id: r.id, action: "submit" })} disabled={st !== "draft" || actionMut.isPending}>
                              送审
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => actionMut.mutate({ id: r.id, action: "approve" })} disabled={st !== "pending" || actionMut.isPending}>
                              通过
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => actionMut.mutate({ id: r.id, action: "reject" })} disabled={st !== "pending" || actionMut.isPending}>
                              驳回
                            </Button>
                            <Button variant="destructive" size="sm" onClick={() => actionMut.mutate({ id: r.id, action: "delete" })} disabled={st === "approved" || actionMut.isPending}>
                              删除
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </PageSection>
    </PageContainer>
  )
}

