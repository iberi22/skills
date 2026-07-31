---
name: claude-design-principles
slug: claude-design-principles
version: 1.1.0
description: Principios de diseño UI/UX distillados del system prompt de Claude Design. Recopila contexto antes de diseñar, ofrece 3+ variantes, evita AI slop. Incluye sistemas de color, tipografía, espaciado y heurísticas de diseño.
license: MIT
original_source: https://github.com/Jane-xiaoer/claude-design-principles
category: design
tags: [design, ui, ux, claude-design, color-system, typography, spacing, heuristics, frontend]
goals:
  - Recopilar contexto de diseño antes de proponer soluciones
  - Generar 3+ variantes de diseño para cada problema
  - Evitar patrones de "AI slop" en diseños
  - Aplicar principios de diseño consistentes (color, tipografía, espaciado)
  - Usar heurísticas de usabilidad (Gestalt, Fitts, Hick)
authors:
  - Jane-xiaoer (repo original)
  - Brahyan Belalcazar (versión estructurada)
---

# Claude Design Principles

> **核心认知**：优秀的设计不是从零猜出来的，是从现有语境里"长"出来的。这个 skill 把 Claude Design 的判断力压缩成可执行 checklist。

---

## ⛔ 三条硬规则（违反就算失败）

### 规则 1：设计前必须先采集语境

不存在"我脑子里有个好主意就开干"。动手前必须至少拿到**一项**：

- 现有 UI kit / design system 文件
- 品牌 tokens（色板、字体栈、间距、圆角规范）
- 参考站点/产品的截图
- 现有代码库里的组件
- 明确的品牌描述文档

**没有以上任何一项 → 必须先问用户要**，或一起确定"视觉 DNA 锚点"（比如"像 Aesop 那种米白 + 衬线字 + 留白"）。从零 mock 是 **last resort**，一旦发生会产出通用 AI slop。

### 规则 2：一次至少给 3 个方案，基础 → 前卫渐进

不允许只给一个方案。每次输出至少：

- **方案 A（规范版）** — 严格遵循已有 design system，零冒险
- **方案 B（进阶版）** — 在 system 基础上加一点变化（配色、版式、排版节奏）
- **方案 C（前卫版）** — 允许跳出 system，尝试新隐喻、novel layout、大胆 typography

把这些作为不同 tabs / 并排 cards / slides 展现，让用户 mix and match。

### 规则 3：AI Slop 清单全部拉黑

这些模式一看就是 AI 生成，**禁止使用**：

- ❌ 大面积渐变背景（紫蓝、粉橙等）
- ❌ 圆角容器 + 左边 4px 色块 accent
- ❌ 用 SVG 自己画插画
- ❌ Inter / Roboto / Arial / Fraunces / 系统字体（除非品牌规定）
- ❌ 堆砌 emoji（除非品牌明确用）
- ❌ 为填充而填充的数据、icon、stat
- ❌ 虚构的"用户评价"、placeholder 肖像
- ❌ 每个 section 都加"信任标记" / "客户 logo"

---

## ❓ Question Templates（采集语境用）

向用户提问时，至少覆盖以下维度：

1. **品牌资产**：是否有 brand guidelines / design system / UI kit？
2. **色板**：主色、辅助色、中性色、语义色（成功/警告/错误）？
3. **字体**：品牌字体、正文字体、字重组合、是否支持多语言？
4. **载体**：网页 / App / 幻灯片 / 海报 / 原型？目标分辨率？
5. **受众**：B2B / B2C？年龄层？专业度？
6. **情绪**：想传达什么感觉？（如：可信、活泼、极简、奢华）
7. **参考**：有没有喜欢的竞品或参考站点？
8. **约束**：有无技术限制（如 Tailwind / Material / 纯 CSS）？
9. **内容**：文案是否 final？图片/插画是否已提供？
10. **交互**：是否需要动画？滚动效果？hover 状态？

---

## 🎨 Color System（色彩系统）

### 基础结构
- **Primary**：品牌主色，用于 CTA、关键操作、链接
- **Secondary**：辅助色，用于标签、次要按钮、装饰
- **Neutral**：灰阶（50-950），用于文本、背景、边框、分隔线
- **Semantic**：Success / Warning / Error / Info，仅用于状态反馈

### 规则
- 使用 OKLCH 或 HSL 定义颜色，确保感知均匀性
- 对比度：正文文本 ≥ 4.5:1（WCAG AA），大文本 ≥ 3:1
- 避免纯黑（`#000000`），使用深灰（如 `#0a0a0a`）降低眩光
- 暗色模式不是"反色"，需单独调暗主色、提亮中性色
- 最多 3 个 accent color，超过会分散注意力

---

## 🔤 Typography System（字体系统）

### 字号阶梯（以 16px 基础）
| Token | Size | Line Height | Usage |
|-------|------|-------------|-------|
| `text-xs` | 12px | 1.5 | 标签、时间戳、辅助说明 |
| `text-sm` | 14px | 1.5 | 表单项、次要文本 |
| `text-base` | 16px | 1.6 | 正文阅读 |
| `text-lg` | 18px | 1.5 | 引言、强调段落 |
| `text-xl` | 20px | 1.4 | 小标题、卡片标题 |
| `text-2xl` | 24px | 1.3 | 区块标题 |
| `text-3xl` | 30px | 1.2 | 页面大标题 |
| `text-4xl+` | 36px+ | 1.1 | Hero / 幻灯片主标题 |

### 规则
- 一个项目最多 **2 个字体家族**：1 个用于标题（display），1 个用于正文（body）
- 行高：正文 1.5–1.7，标题 1.1–1.3，UI 元素 1.25
- 字重：正文用 400–500，标题用 600–700，避免 300 以下用于长文本
- 每行最佳 45–75 个字符（桌面 60–75，移动 35–50）
- 避免 `text-align: justify` 在屏幕上使用

---

## 📐 Spacing Rhythm（间距节奏）

### 基础单位：4px / 8px
使用 4 的倍数构建统一 rhythm：

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 4px | 图标与文本间距、紧凑内边距 |
| `space-2` | 8px | 小按钮内边距、行内元素 |
| `space-3` | 12px | 表单元素间距 |
| `space-4` | 16px | 卡片内边距、段落间距 |
| `space-6` | 24px | 区块内部间距 |
| `space-8` | 32px | 卡片之间间距 |
| `space-12` | 48px | 大区块间距 |
| `space-16` | 64px | Section 间距 |

### 规则
- 圆角：UI 元素 4–8px，卡片 12–16px，全圆角仅用于 pill / badge
- 阴影：最多 3 层（`sm` / `md` / `lg`），避免纯黑阴影，用带品牌色相的深色
- 对齐：优先左对齐，慎用居中（仅用于短标题或 CTA）
- 亲密性：相关元素间距小，无关元素间距大

---

## 🧠 Design Heuristics（设计启发式）

### Gestalt 原理
- **Proximity（接近性）**：相关元素放一起，不相关拉开距离
- **Similarity（相似性）**：同层级元素用相同颜色/大小/形状表达
- **Continuation（连续性）**：人眼沿直线/曲线移动，利用排版引导阅读
- **Common Region（共同区域）**：用背景/边框/阴影将相关内容分组
- **Figure-Ground（图底关系）**：确保前景元素与背景有足够对比

### Fitts's Law（菲茨定律）
- 关键操作按钮要**大**且放在**容易触及**的位置
- 屏幕边缘和角落是"无限大"的目标（适合放菜单/返回）
- 移动端底部按钮 ≥ 44×44px，桌面主要 CTA ≥ 48px 高度

### Hick's Law（希克定律）
- 选项越多，决策时间越长
- 每屏最多 5–7 个主要选项
- 用分组、递进披露（progressive disclosure）减少一次性认知负荷

### 其他关键原则
- **Miller's Law**：工作记忆容量 7±2，复杂信息分块呈现
- **Jakob's Law**：用户 99% 的时间花在别人家的产品上，遵循平台惯例
- **Aesthetic-Usability Effect**：美观的界面被认为更易用，但美观不能替代可用性
- **Law of Proximity**：按钮与反馈要紧邻，错误提示靠近输入框

---

## ✅ Checklist Pre-Entrega（交付前自检）

- [ ] 已采集至少一项品牌资产或视觉锚点
- [ ] 提供了 ≥3 个方案（规范 / 进阶 / 前卫）
- [ ] 过一遍 AI Slop 清单，无违规项
- [ ] 所有正文文本对比度 ≥ 4.5:1
- [ ] 字号阶梯清晰，无小于 12px 的常规文本
- [ ] 触控目标 ≥ 44px（移动端）
- [ ] 间距使用 4/8px 倍数，无随意数值
- [ ] 每行字符数在 45–75 之间
- [ ] 阴影/圆角/色温在整个文档中一致
- [ ] 已询问用户反馈，未直接交付单一方案

---

> **最后提醒**：设计失败的 90% 来源不是审美不够，是**没问清楚 + 语境不够 + 只给一个方案**。把这份 skill 当 checklist，每一步都过。
