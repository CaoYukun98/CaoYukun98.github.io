# 主页自动更新规则

这个仓库是 <https://caoyukun98.github.io/> 的源码（Jekyll / AcadHomepage）。
本文件定义“收到用户信息 → 更新主页 → 校验 → 提交 → 发布”的固定流程。

## 触发方式

当前**没有启用定时任务**，只有两种手动触发：

1. **对话触发（推荐）**：用户在对话里直接发来要更新的信息，立即按本文件处理。
2. **收件箱触发**：把信息写进 `automation/inbox.md` 的 `## 待处理` 下，
   然后说“处理收件箱”。需要每天自动检查时，再让助手加定时任务。

## 输入格式

自然语言即可，不强制格式。建议写清“类型 + 内容”，例如：

```text
2026-11-05
- 新闻：获得 XXX 奖。
- 论文：ACL 2027 录用，题目 ...，作者 ...，链接 ...。
- 荣誉：入选 XXX。
```

无法判断类型时，按“新闻”处理，或写入 `automation/questions.md` 等用户确认，**不要编造**。

## 内容映射

只改内容，不改主题、布局和样式，除非用户明确要求。

| 类型 | 位置 | 规则 |
| --- | --- | --- |
| 新闻 / 动态 | `_pages/about.md` 的 `# 📰 News` | 没有该节时，在 `# 📝 Publications` 前新建；最新在上；格式 `- **YYYY.MM** 内容。` |
| 论文 | `_pages/about.md` 对应论文列表 | 一作/通讯放入 `🟦 First/Corresponding Author`，其他放入 `⬜ Other Publications`；新论文放对应列表最上面；保留现有 `[ACL 26-Main (CCF-A)]` 风格 |
| 荣誉 | `_pages/about.md` 的 `# 🎖 Honors and Awards` | 最新在上，格式 `- YYYY **名称** at 机构.` |
| 简介 / 任职 | `_pages/about.md` 的 `# 👦 About me` | 保持原有段落与链接风格；不整段重写，只改相关句子 |
| 联系方式 / 头像 / 社交链接 | `_config.yml` 的 `author:` | 只改对应字段，保留注释和缩进 |
| 教育经历 | `_pages/about.md` 的 `# 📖 Educations` | 保持倒序和时间格式 |

### 论文字段的最低要求

新增论文至少需要：**会议/期刊 + 年份 + 论文题目 + 完整作者顺序 + 链接**。
缺作者、缺链接时先不要发布，把缺什么写进 `automation/questions.md`。

- 作者列表中把 `Yukun Cao` 加粗；一作/通讯按原文加 `#` 或 `Co-First`。
- 会议/期刊名用斜体，会议全称按现有风格补全。
- 同一篇论文不要重复添加；先按题目在 `_pages/about.md` 中检索。

## 固定流程

1. 读 `automation/inbox.md` 的 `## 待处理`（或直接读用户消息）。
2. 查重，确定每条信息的类型和目标位置。
3. 编辑 `_pages/about.md`（必要时 `_config.yml`）。
4. 运行 `python3 automation/validate.py`，必须通过。
5. 把已处理内容移到 `automation/archive/YYYY-MM.md`，并在 `automation/inbox.md` 清空 `## 待处理`。
6. 提交并尝试发布：

   ```bash
   bash automation/publish.sh "Update homepage: <一句话摘要>"
   ```

   - 退出码 `0`：已提交并推送成功。
   - 退出码 `2`：已本地提交，但缺 GitHub 凭证，未推送。告知用户“已保存到本地，尚未上线”。
   - 其他非零：失败，保留现场，不要强推。

7. 没有待处理内容或没有实际改动时：**不提交、不推送、不打扰用户**。

## 硬性限制

- 不删除已有论文、荣誉、教育经历，除非用户明确说“删除”。
- 不编造论文、奖项、日期、链接、合作者。
- 不改 `_layouts/`、`_includes/`、`_sass/`、`assets/`，除非用户要求改版。
- 不执行 `git push --force`，不改写历史。
- 不把 token 写进仓库、URL、提交信息或日志。
- 发布前必须通过 `validate.py` 和 `git diff --check`。
- 一次提交只做一件事：主页内容更新，提交信息用 `Update homepage: ...`。

## 凭证

发布需要仓库 `caoyukun98/caoyukun98.github.io` 的写权限，二选一：

- **Deploy key（当前使用）**：私钥在 `automation/deploy_key`，公钥已加到仓库
  `Settings → Deploy keys` 并勾选 `Allow write access`。
- **Fine-grained PAT（备选）**：token 只放在 `automation/.github-token`。

两者都在 `.gitignore` 中，不要贴到对话里，也不要用 `git add -f` 加进仓库。
没有可用凭证时，流程仍会完成本地修改和提交，只是不推送。
