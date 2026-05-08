import { PageContainer, PageHeader, PageSection } from "@/components/ui/page-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function PlaceholderPage({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string
  title: string
  description?: string
}) {
  return (
    <PageContainer className="flex-1 space-y-6">
      <PageHeader eyebrow={eyebrow} title={title} description={description ?? "该页面正在还原中（UI 已对齐原系统菜单结构）。"} />
      <PageSection>
        <Card>
          <CardHeader>
            <CardTitle>提示</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            当前仅完成导航与页面框架。下一步将把该模块的表单/列表与 xtck_deploy 的数据结构一比一补齐。
          </CardContent>
        </Card>
      </PageSection>
    </PageContainer>
  )
}

