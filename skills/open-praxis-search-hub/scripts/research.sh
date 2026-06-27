#!/bin/bash
# 安全研究工作流：Exa 搜索 + gh-lookup + Ollama 分析
# 完全免费，国内可用，不触发 GitHub 风控

set -e

SEARCH_HUB="/Users/alex/Documents/myCode/skills/praxis-skills/skills/praxis-search-hub/scripts/safe_search.py"
OLLAMA_URL="http://localhost:11434/v1/chat/completions"
MODEL="qwen2.5:14b"

# 颜色输出
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    echo "用法: research.sh <查询> [选项]"
    echo ""
    echo "选项:"
    echo "  --web              只搜索网页 (Exa)"
    echo "  --github REPO      查看 GitHub 仓库详情 (owner/repo)"
    echo "  --analyze          用 Ollama 分析结果"
    echo "  --full             完整流程：搜索 + 分析"
    echo "  --domain DOMAIN    垂直搜索 (finance/academic/code 等)"
    echo ""
    echo "示例:"
    echo "  research.sh \"DeerFlow 字节跳动\""
    echo "  research.sh --github bytedance/deer-flow"
    echo "  research.sh \"AI agent framework\" --full"
    echo "  research.sh \"AAPL\" --domain finance"
    exit 0
}

web_search() {
    echo -e "${BLUE}🔍 搜索: $1${NC}"
    python3 "$SEARCH_HUB" web "$1" --limit 5
}

anysearch_vertical() {
    echo -e "${BLUE}🔍 垂直搜索 ($1): $2${NC}"
    python3 "$SEARCH_HUB" anysearch "$2" --domain "$1" --limit 5
}

github_lookup() {
    echo -e "${BLUE}📦 GitHub: $1${NC}"
    python3 "$SEARCH_HUB" gh-lookup "$1"
}

ollama_analyze() {
    echo -e "${BLUE}🤖 分析中...${NC}"
    # 去除 ANSI 颜色代码，截取前 2000 字符避免超出 token 限制
    CONTENT=$(echo "$1" | sed 's/\x1b\[[0-9;]*m//g' | head -c 2000)
    # 转义 JSON 特殊字符
    CONTENT_ESCAPED=$(echo "$CONTENT" | python3 -c "import sys; print(sys.stdin.read().replace('\\\\', '\\\\\\\\').replace('\"', '\\\\\"').replace('\n', '\\\\n').replace('\r', ''))")
    curl -s "$OLLAMA_URL" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"$MODEL\",
            \"messages\": [{\"role\": \"user\", \"content\": \"分析这个项目，包括技术栈、适用场景、优缺点：$CONTENT_ESCAPED\"}],
            \"max_tokens\": 500
        }" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'choices' in data:
        print(data['choices'][0]['message']['content'])
    elif 'error' in data:
        print('错误:', data['error'])
    else:
        print('响应:', json.dumps(data, ensure_ascii=False)[:500])
except Exception as e:
    print('解析错误:', e)
"
}

# 安全研究工作流（排除 GitHub 搜索，防止风控）
safe_research() {
    echo -e "${GREEN}=== 安全研究: $1 ===${NC}"
    echo -e "${BLUE}🔍 搜索 (Exa)...${NC}"
    RESULT=$(web_search "$1" 2>&1)
    echo "$RESULT"
    echo -e "\n${BLUE}🤖 分析 (Ollama)...${NC}"
    ollama_analyze "$RESULT"
}

# 主逻辑
if [ $# -eq 0 ]; then
    usage
    exit 1
fi

QUERY=""
REPO=""
DOMAIN=""
MODE="web"

while [ $# -gt 0 ]; do
    case "$1" in
        --web)
            MODE="web"
            shift
            ;;
        --github)
            MODE="github"
            REPO="$2"
            shift 2
            ;;
        --analyze)
            MODE="analyze"
            shift
            ;;
        --full)
            MODE="full"
            shift
            ;;
        --domain)
            MODE="domain"
            DOMAIN="$2"
            shift 2
            ;;
        *)
            QUERY="$1"
            shift
            ;;
    esac
done

case "$MODE" in
    web)
        if [ -z "$QUERY" ]; then
            echo "错误: 请提供搜索查询"
            exit 1
        fi
        web_search "$QUERY"
        ;;
    github)
        if [ -z "$REPO" ]; then
            echo "错误: 请提供仓库名 (owner/repo)"
            exit 1
        fi
        github_lookup "$REPO"
        ;;
    analyze)
        if [ -z "$QUERY" ]; then
            echo "错误: 请提供分析内容"
            exit 1
        fi
        ollama_analyze "$QUERY"
        ;;
    domain)
        if [ -z "$QUERY" ]; then
            echo "错误: 请提供搜索查询"
            exit 1
        fi
        if [ -z "$DOMAIN" ]; then
            echo "错误: 请提供域名 (finance/academic/code 等)"
            exit 1
        fi
        anysearch_vertical "$DOMAIN" "$QUERY"
        ;;
    full)
        if [ -z "$QUERY" ]; then
            echo "错误: 请提供搜索查询"
            exit 1
        fi
        echo -e "${GREEN}=== 步骤 1: 搜索 ===${NC}"
        RESULT=$(web_search "$QUERY" 2>&1)
        echo "$RESULT"

        echo -e "\n${GREEN}=== 步骤 2: 分析 ===${NC}"
        ollama_analyze "$RESULT"
        ;;
esac
