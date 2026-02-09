# MonkeyUI MCP Tools Description

[中文版本](#中文版本) | [English Version](#english-version)

---

## English Version

### Overview

MonkeyUI implements an MCP (Model Context Protocol) server that exposes design system data as tools for AI coding assistants like GitHub Copilot, Cursor, and Claude Desktop. Each design system can be independently accessed via its own API key using the Streamable HTTP protocol.

### Architecture

The MCP server implementation consists of three main components:

1. **`mcp_server.py`** - FastMCP-based server using the official MCP Python SDK
2. **`server.py`** - Core MCP server logic and tool definitions
3. **`views.py`** - REST API and Streamable HTTP protocol endpoints

### Available MCP Tools

MonkeyUI provides **2 primary MCP tools** for each design system:

#### 1. `get_design_system`

**Description:**
Get the complete design system including all design tokens (colors, typography, spacing, etc.)

**Purpose:**
This tool provides access to all design tokens in the design system, enabling AI coding assistants to generate code that adheres to the design system's specifications.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Output:**
Returns a JSON object containing:
- `name` - Design system name
- `description` - Design system description
- `colors` - Color palette (primary, secondary, background, surface, functional tokens)
- `typography` - Font settings (family, weight, size)
- `shadowDepth` - Shadow depth level

**Example Response:**
```json
{
  "name": "Cyberpunk Design System",
  "description": "High-contrast futuristic design with neon accents",
  "colors": {
    "primary": "#FF0080",
    "secondary": "#00FFFF",
    "background": "#0A0A0A",
    "surface": "#1A1A1A"
  },
  "typography": {
    "fontFamily": "Inter, sans-serif",
    "fontWeight": 600,
    "baseFontSize": 16
  },
  "shadowDepth": 2
}
```

#### 2. `get_aesthetic_guidance`

**Description:**
Get the aesthetic guidance context for the design system. Returns high-level design soul invariants (mood, material language, color grammar, layout grammar, component vocabulary) and variation knobs for generating pages that share the same visual soul without cloning.

**Purpose:**
This tool provides rich aesthetic analysis that captures the "soul" of the design system. It helps AI assistants understand not just the technical tokens, but the philosophical and aesthetic principles behind the design. This enables generation of pages that feel cohesive with the brand without being exact clones.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Output:**
Returns a Markdown document containing:
- **Soul Invariants** - Core design principles that must remain constant
  - Mood and atmosphere
  - Material language
  - Color grammar
  - Layout grammar
  - Component vocabulary
- **Variation Knobs** - Degrees of freedom for creating unique pages
- **Anti-patterns** - What to avoid to preserve design soul

**Example Response:**
```markdown
# Aesthetic Guidance: Cyberpunk Design System

## Soul Invariants

### Mood
High-energy, futuristic, rebellious with a dark undertone

### Material Language
- Sharp edges and angular shapes
- Glowing neon outlines
- Dark, high-contrast backgrounds
- Holographic effects

### Color Grammar
- Dominant: Deep blacks (#0A0A0A) for backgrounds
- Accent: Hot pink (#FF0080) and cyan (#00FFFF) for CTAs
- Never use: Pastels, earth tones

### Layout Grammar
- Asymmetric compositions
- Diagonal lines and cuts
- Dense information hierarchy
- Grid overlays

## Variation Knobs
- Neon color intensity (70-100%)
- Grid opacity (10-30%)
- Animation speed
- Content density

## Anti-patterns
- Do NOT use rounded corners
- Avoid soft gradients
- Never center everything
- No minimalist white space
```

### MCP Server Configuration

#### Server Naming Convention
Each design system gets a unique MCP server name:
```
monkeyui-{design-system-name-in-kebab-case}
```

Example: `monkeyui-cyberpunk-design-system`

#### Supported Protocols

**Streamable HTTP Protocol (Recommended)**
- Endpoint: `POST /api/v1/design-systems/mcp/{design_system_id}/`
- Supports: GitHub Copilot, Cursor, web-based MCP clients
- Authentication: Bearer token via `Authorization` header or `X-API-Key` header

#### MCP Methods Supported

1. **initialize** - Initialize MCP connection
2. **tools/list** - List available tools
3. **tools/call** - Execute a tool call
4. **notifications/** - Handle notifications (no response needed)

### Authentication

All MCP requests require authentication via API keys:

1. Users create API keys in the MonkeyUI web interface (Settings → API Keys)
2. API keys are associated with user accounts
3. Each request validates:
   - API key is active and not expired
   - User owns the requested design system
   - Last used timestamp is updated

### Integration Examples

#### GitHub Copilot Configuration
Add to `.vscode/mcp.json`:
```json
{
  "servers": {
    "monkeyui-cyberpunk": {
      "type": "http",
      "url": "https://your-domain.com/api/v1/design-systems/mcp/{design-system-id}/",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

#### Cursor Configuration
Add to `~/.cursor/mcp.json` or `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "monkeyui-cyberpunk": {
      "url": "https://your-domain.com/api/v1/design-systems/mcp/{design-system-id}/",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

### REST API Endpoints

For backward compatibility and debugging, MonkeyUI also provides REST endpoints:

- **GET** `/api/design-system/mcp/{design_system_id}/tools/` - List tools
- **POST** `/api/design-system/mcp/{design_system_id}/call/` - Call a tool
- **GET** `/api/v1/design-systems/mcp/{design_system_id}/` - Get server info

### Use Cases

1. **Design-System-Driven Development**
   - AI assistants can query design tokens while generating components
   - Ensures consistent styling across all generated code

2. **Brand-Consistent Page Generation**
   - Use `get_aesthetic_guidance` to understand design philosophy
   - Generate pages that feel cohesive without cloning references

3. **Design Token Synchronization**
   - Keep code in sync with evolving design systems
   - AI assistants always use latest design tokens

4. **Multi-Brand Projects**
   - Connect different design systems to different projects
   - AI assistants automatically use the right brand's design system

---

## 中文版本

### 概述

MonkeyUI 实现了一个 MCP（Model Context Protocol，模型上下文协议）服务器，将设计系统数据作为工具暴露给 AI 编程助手，如 GitHub Copilot、Cursor 和 Claude Desktop。每个设计系统都可以通过自己的 API 密钥独立访问，使用 Streamable HTTP 协议。

### 架构

MCP 服务器实现由三个主要组件组成：

1. **`mcp_server.py`** - 基于官方 MCP Python SDK 的 FastMCP 服务器
2. **`server.py`** - 核心 MCP 服务器逻辑和工具定义
3. **`views.py`** - REST API 和 Streamable HTTP 协议端点

### 可用的 MCP 工具

MonkeyUI 为每个设计系统提供 **2 个主要 MCP 工具**：

#### 1. `get_design_system`

**描述：**
获取完整的设计系统，包括所有设计令牌（颜色、字体排版、间距等）

**用途：**
此工具提供对设计系统中所有设计令牌的访问，使 AI 编程助手能够生成符合设计系统规范的代码。

**输入结构：**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**输出：**
返回一个 JSON 对象，包含：
- `name` - 设计系统名称
- `description` - 设计系统描述
- `colors` - 色彩调色板（主色、辅色、背景色、表面色、功能色）
- `typography` - 字体设置（字体系列、字重、大小）
- `shadowDepth` - 阴影深度级别

**示例响应：**
```json
{
  "name": "赛博朋克设计系统",
  "description": "高对比度未来主义设计，带有霓虹灯强调",
  "colors": {
    "primary": "#FF0080",
    "secondary": "#00FFFF",
    "background": "#0A0A0A",
    "surface": "#1A1A1A"
  },
  "typography": {
    "fontFamily": "Inter, sans-serif",
    "fontWeight": 600,
    "baseFontSize": 16
  },
  "shadowDepth": 2
}
```

#### 2. `get_aesthetic_guidance`

**描述：**
获取设计系统的美学指导上下文。返回高层次的设计灵魂不变量（情绪基调、材质语言、色彩语法、布局语法、组件词汇表）和变体旋钮，用于生成共享相同视觉灵魂但不克隆的页面。

**用途：**
此工具提供丰富的美学分析，捕捉设计系统的"灵魂"。它帮助 AI 助手理解的不仅是技术令牌，还有设计背后的哲学和美学原则。这使得能够生成与品牌感觉一致的页面，而不是精确的克隆。

**输入结构：**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**输出：**
返回一个 Markdown 文档，包含：
- **灵魂不变量** - 必须保持不变的核心设计原则
  - 情绪和氛围
  - 材质语言
  - 色彩语法
  - 布局语法
  - 组件词汇表
- **变体旋钮** - 创建独特页面的自由度
- **反模式** - 为了保持设计灵魂应该避免的事项

**示例响应：**
```markdown
# 美学指导：赛博朋克设计系统

## 灵魂不变量

### 情绪基调
高能量、未来主义、带有暗黑基调的叛逆感

### 材质语言
- 锐利的边缘和棱角形状
- 发光的霓虹轮廓
- 深色、高对比度背景
- 全息效果

### 色彩语法
- 主导色：深黑色 (#0A0A0A) 用于背景
- 强调色：亮粉色 (#FF0080) 和青色 (#00FFFF) 用于 CTA
- 禁止使用：粉彩色、大地色调

### 布局语法
- 非对称构图
- 对角线和切割
- 密集的信息层次
- 网格叠加

## 变体旋钮
- 霓虹色彩强度 (70-100%)
- 网格不透明度 (10-30%)
- 动画速度
- 内容密度

## 反模式
- 不要使用圆角
- 避免柔和的渐变
- 永远不要居中所有内容
- 不要使用极简的留白
```

### MCP 服务器配置

#### 服务器命名规范
每个设计系统都有一个唯一的 MCP 服务器名称：
```
monkeyui-{设计系统名称-短横线分隔}
```

示例：`monkeyui-cyberpunk-design-system`

#### 支持的协议

**Streamable HTTP 协议（推荐）**
- 端点：`POST /api/v1/design-systems/mcp/{design_system_id}/`
- 支持：GitHub Copilot、Cursor、基于 Web 的 MCP 客户端
- 身份验证：通过 `Authorization` 头或 `X-API-Key` 头的 Bearer token

#### 支持的 MCP 方法

1. **initialize** - 初始化 MCP 连接
2. **tools/list** - 列出可用工具
3. **tools/call** - 执行工具调用
4. **notifications/** - 处理通知（无需响应）

### 身份验证

所有 MCP 请求都需要通过 API 密钥进行身份验证：

1. 用户在 MonkeyUI Web 界面中创建 API 密钥（设置 → API 密钥）
2. API 密钥与用户账户关联
3. 每个请求验证：
   - API 密钥活跃且未过期
   - 用户拥有请求的设计系统
   - 更新最后使用时间戳

### 集成示例

#### GitHub Copilot 配置
添加到 `.vscode/mcp.json`：
```json
{
  "servers": {
    "monkeyui-cyberpunk": {
      "type": "http",
      "url": "https://your-domain.com/api/v1/design-systems/mcp/{design-system-id}/",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

#### Cursor 配置
添加到 `~/.cursor/mcp.json` 或 `.cursor/mcp.json`：
```json
{
  "mcpServers": {
    "monkeyui-cyberpunk": {
      "url": "https://your-domain.com/api/v1/design-systems/mcp/{design-system-id}/",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

### REST API 端点

为了向后兼容和调试，MonkeyUI 还提供 REST 端点：

- **GET** `/api/design-system/mcp/{design_system_id}/tools/` - 列出工具
- **POST** `/api/design-system/mcp/{design_system_id}/call/` - 调用工具
- **GET** `/api/v1/design-systems/mcp/{design_system_id}/` - 获取服务器信息

### 使用场景

1. **设计系统驱动的开发**
   - AI 助手在生成组件时可以查询设计令牌
   - 确保所有生成的代码样式一致

2. **品牌一致的页面生成**
   - 使用 `get_aesthetic_guidance` 了解设计哲学
   - 生成感觉一致的页面，而不是克隆参考

3. **设计令牌同步**
   - 使代码与不断演进的设计系统保持同步
   - AI 助手始终使用最新的设计令牌

4. **多品牌项目**
   - 将不同的设计系统连接到不同的项目
   - AI 助手自动使用正确品牌的设计系统
