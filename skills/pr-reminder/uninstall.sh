#!/bin/bash
# PR Reminder Skill 卸载脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SKILL_NAME="pr-reminder"
SKILLS_DIR="$HOME/.claude/skills"

echo -e "${YELLOW}=== PR Reminder Skill 卸载 ===${NC}"
echo ""

# 检查是否安装
if [ ! -L "$SKILLS_DIR/$SKILL_NAME" ]; then
    echo -e "${RED}Skill 未安装（软链接不存在）${NC}"
    exit 0
fi

# 删除软链接
echo "删除软链接..."
rm "$SKILLS_DIR/$SKILL_NAME"

# 验证
if [ ! -L "$SKILLS_DIR/$SKILL_NAME" ]; then
    echo -e "${GREEN}✅ 卸载成功！${NC}"
    echo ""
    echo "注意：Skill 源文件仍然保留在:"
    echo "  $(pwd)"
else
    echo -e "${RED}❌ 卸载失败${NC}"
    exit 1
fi
