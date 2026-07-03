# Demo 页面核心需求文档

> 每次修改 demo 页面必须对照此文件，不允许删除。每次修改 demo 页面都需要把此文件内容列为核心提示词。

## 核心规则

1. 每次修改后必须完整检查页面功能，不允许只修补一个问题而不验证其他功能是否正常。
2. 每次修改 demo 页面都需要把此文件内容列为核心提示词。
3. 每次出错记录到本文件「错误记录」章节，解决后附在错误记录后。

## 功能需求

### 1. 独立页面

- Demo 页面是独立 HTML 页面（demo.html），通过 `/demo_hr` 路由访问
- 案例对比页面也是独立页面（case_study.html），通过 `/case-study` 路由访问
- PPT 第4页 Hub 页通过卡片链接跳转到这两个独立页面
- 独立页面有「← 返回PPT」链接，跳转到 `/?slide=4`（回到 Hub 页）

### 2. 双栏对比布局

- 左侧：通用 AI（MiMo 多模态）
- 右侧：企业 AI（G5 Pipeline：多模态 + 评分引擎 + JD 匹配）
- 上传简历后，两个分析同时进行

### 3. 文件上传

- **仅支持 PDF 格式**
- PDF 文件直接读取 base64 传给后端，由 MiMo 多模态看图分析，**不需要前端提取文字**
- 上传后文件名变成可点击链接，新标签页打开预览（blob URL）
- 选择文件按钮样式符合 PPT 主题色

### 4. 通用 AI（左栏）

- 调用 `/r/resume/analyze`（MiMo 多模态，文本+PDF 图片）
- 接受 `{resume: text}` 或 `{file_base64: ..., filename: ...}`
- 返回 Markdown 格式分析结果
- 前端用 `renderMarkdown()` 渲染为 HTML（支持 `##`、`###`、`**`、`- `、`1. `）
- 用户对话框必须显示发送给 AI 的提示词原文："请作为一名拥有10年经验的资深HR招聘专家，分析这份简历：给出各维度评分（学历/经验/能力/细节/表达）、总评分、是否推荐面试及理由，并列出3个面试重点考察问题。"

### 5. 企业 AI（右栏）

- 调用 `/r/resume/enterprise-analyze`（异步模式，立即返回 task_id）
- **PDF 直接交给 G5 脚本分析，不做任何前端预处理**
- **禁止硬编码，必须分析用户实际上传的文件**
- 调用 `/r/resume/task/<task_id>` 每 2 秒轮询结果
- 状态提示文字：「正在调用企业AI引擎进行多维度分析...」（不能有技术术语如"后台运行不会超时"）
- 失败时显示「🔄 重试」按钮
- **脚本输出结果不能修改，只能渲染显示效果**
- **所有字段必须完整显示：basic_info(gender/age/education/is_full_time/school/major/relevant_experience_years/contact)、_matched_position、_position_reason、_positions_count、scores(含 deduction/weighted)、jd_check、work_experience_analysis、highlights、warnings、recommendation、interview_questions、preliminary_questions**
- **所有卡片不折叠，全部展开**

#### 5.1 基本信息卡片

- 姓名、学历、院校、经验年限

#### 5.2 匹配岗位

- 最佳匹配岗位名称
- **分步展示：先显示读取到的在招岗位列表，再显示匹配到的岗位名称，最后输出分析结果**

#### 5.3 综合评分表

- 学历匹配 X/10
- 经验匹配 X/20
- 核心能力 X/30
- 细节审查 X/20
- 表达沟通 X/20
- 加分项 +N（绿色）
- 预警扣分 -N（红色）
- 综合评分 N/100

#### 5.4 推荐意见

#### 5.5 候选人亮点（可展开卡片）

#### 5.6 工作经历分析（可展开卡片）

- 每段经历显示期间、公司、职位、摘要、引文解读

#### 5.7 JD 匹配详情（可展开卡片）

- 学历要求、经验要求
- 技能匹配（格式化对象数组，不能显示 `[object Object]`）
- 加分项（同上）

#### 5.8 预警（可展开卡片）

#### 5.9 面试问题（可展开卡片）

- 初筛问题 + 深度问题

### 6. 评分标准查看

- 右侧面板标题栏有「📋 查看评分标准」链接
- 点击后弹出新窗口，显示当次分析使用的：
  - 匹配岗位的 JD 及评分标准
  - 全局评分标准
- **评分标准内容需要 Markdown 渲染显示**

### 7. 页面样式

- 复用 PPT 主题 CSS 变量（--paper, --accent, --ink, --grey-1 等）
- 卡片默认全部展开，不需要折叠
- **左右两个面板都能独立上下滚动查看完整分析内容**
- 标题下方显示模型名称：`本次测试使用模型均为 MiMo V2.5`
- 移动端双栏变上下堆叠
- 无白边、无底部导航

### 8. API 端点（使用 /r/ 前缀绕过 Cloudflare WAF）

- `/r/resume/analyze` → 通用 AI（支持 file_base64 和 resume）
- `/r/resume/enterprise-analyze` → 企业 AI（异步，支持 file_base64 和 resume）
- `/r/resume/task/<id>` → 查询异步任务结果

### 9. retryEnterprise 重试功能

- 保留已上传的文件数据
- 重新发起企业 AI 分析任务
- 需要能正确访问 resumePdfBase64 和 resumeText

## 验证清单（每次修改后必须检查）

- [ ]  页面加载：demo 页面 HTTP 200
- [ ]  JS 语法：script 标签 1 开 1 闭，无重复
- [ ]  上传 PDF（文字型）：通用 AI 和企业 AI 都能正常分析
- [ ]  上传 PDF（图片型）：企业 AI 多模态正常分析，通用 AI 也有结果
- [ ]  文件上传仅支持 PDF 格式
- [ ]  通用 AI 对话框显示完整提示词
- [ ]  评分表：子项 + 加分 - 扣分 = 综合评分
- [ ]  JD 匹配：技能列表不显示 [object Object]
- [ ]  评分标准链接：点击能弹出窗口，内容 Markdown 渲染
- [ ]  简历预览：文件名可点击打开
- [ ]  返回PPT：链接跳转到 /?slide=4
- [ ]  左右面板都能独立上下滚动
- [ ]  企业 AI 分析的是用户上传的文件，非硬编码
- [ ]  失败重试：🔄 按钮能重新发起分析
- [ ]  移动端：双栏变上下堆叠，无白边

## 错误记录

> 格式：`[日期] 错误描述 → 原因 → 解决方案`

- [2026-06-23] 502 超时 → Cloudflare 拦截大 POST + MiMo 调用耗时长 → 改为异步轮询 + /r/ 前缀绕过 WAF
- [2026-06-23] 通用 AI 返回全 0 分 → 端点未处理 file_base64，收到空文本生成空白 PDF → 端点增加 file_base64 直存路径
- [2026-06-23] 企业 AI 卡片互相遮挡、无法滚动 → CSS flex-shrink:0 + overflow:hidden → 改为 display:block + overflow-y:auto
- [2026-06-23] demo 页面 JS 不执行 → `<script>` 标签重复两遍 → 删除重复标签
- [2026-06-23] 通用 AI 用户消息不显示提示词 → 简化时删除了提示词显示 → ✅ 已修复，重写时恢复
- [2026-06-23] 仅支持 PDF 格式 → 代码仍处理 .txt/.md 分支 → ✅ 已修复，重写后仅 accept=".pdf"
- [2026-06-23] 企业 AI 卡片互相遮挡、无法滚动 → CSS flex-shrink:0 + overflow:hidden → ✅ 已修复
- [2026-06-23] 评分标准弹窗显示纯文本 → 未渲染 markdown → ✅ 已修复，弹窗使用 renderMarkdown
- [2026-06-23] 左右面板不能独立滚动 → 仅右栏有 overflow-y:auto → ✅ 已修复，两栏 chat-area 均有 overflow-y:auto
- [2026-06-23] 通用 AI 返回「简历内容不足」→ 服务器 app.py 未同步 file_base64 处理 → ✅ 已修复并部署
- [2026-06-23] app.py 缩进错误导致 Flask 崩溃 → else 语句块未缩进 → ✅ 已修复
- [2026-06-23] 企业 AI 遗漏字段 → _position_reason、_positions_count、gender、age、major 等未显示 → ✅ 已补全
