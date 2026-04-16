#!/bin/bash
# PR Reminder Skill 安装脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_NAME="pr-reminder"
SKILLS_DIR="$HOME/.claude/skills"

echo -e "${GREEN}=== PR Reminder Skill 安装 ===${NC}"
echo ""

# 检查 skills 目录是否存在
if [ ! -d "$SKILLS_DIR" ]; then
    echo -e "${YELLOW}创建 skills 目录: $SKILLS_DIR${NC}"
    mkdir -p "$SKILLS_DIR"
fi

# 检查是否已经安装
if [ -L "$SKILLS_DIR/$SKILL_NAME" ]; then
    echo -e "${YELLOW}Skill 已经安装（软链接已存在）${NC}"
    echo "删除旧链接..."
    rm "$SKILLS_DIR/$SKILL_NAME"
elif [ -d "$SKILLS_DIR/$SKILL_NAME" ]; then
    echo -e "${YELLOW}Skill 目录已存在，但不是软链接${NC}"
    echo "请先手动删除: $SKILLS_DIR/$SKILL_NAME"
    exit 1
fi

# 创建软链接
echo "创建软链接..."
ln -s "$SCRIPT_DIR" "$SKILLS_DIR/$SKILL_NAME"

# 验证
if [ -L "$SKILLS_DIR/$SKILL_NAME" ]; then
    echo -e "${GREEN}✅ 安装成功！${NC}"
    echo ""
    echo "Skill 位置: $SCRIPT_DIR"
    echo "软链接位置: $SKILLS_DIR/$SKILL_NAME"
    echo ""
    echo "你现在可以在 Claude Code 中使用这个 skill 了！"
    echo ""
    echo "使用示例："
    echo "  - 请帮我生成今天的 PR 状态报告"
    echo "  - 检查一下有哪些 PR 需要提醒"
    echo "  - 看看 pending 的 PR 进展如何"
else
    echo -e "${YELLOW}❌ 安装失败${NC}"
    exit 1
fi
