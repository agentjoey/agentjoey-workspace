#!/bin/bash
# Agentjoey Workspace - Vercel Deploy Script
# Usage: ./scripts/deploy.sh [website|docs|all]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}→${NC} $1"
}

# Check if vercel is installed
if ! command -v vercel &> /dev/null; then
    print_error "Vercel CLI not found. Install with: npm i -g vercel"
    exit 1
fi

# Check login status
if ! vercel whoami &> /dev/null; then
    print_error "Not logged in to Vercel. Run: vercel login"
    exit 1
fi

DEPLOY_TARGET=${1:-all}

case $DEPLOY_TARGET in
    website|web)
        print_info "Deploying Website..."
        cd apps/website
        vercel --prod
        print_status "Website deployed!"
        ;;
    
    docs|documentation)
        print_info "Deploying Documentation..."
        cd apps/documentation
        vercel --prod
        print_status "Documentation deployed!"
        ;;
    
    all)
        print_info "Deploying all applications..."
        
        # Deploy Website
        print_info "Deploying Website..."
        cd apps/website
        if vercel --prod; then
            print_status "Website deployed successfully!"
        else
            print_error "Website deployment failed"
        fi
        cd ../..
        
        # Deploy Documentation
        print_info "Deploying Documentation..."
        cd apps/documentation
        if vercel --prod; then
            print_status "Documentation deployed successfully!"
        else
            print_error "Documentation deployment failed"
        fi
        cd ../..
        
        print_status "All deployments complete!"
        ;;
    
    *)
        echo "Usage: ./scripts/deploy.sh [website|docs|all]"
        echo ""
        echo "Commands:"
        echo "  website    Deploy apps/website"
        echo "  docs       Deploy apps/documentation"
        echo "  all        Deploy all applications (default)"
        exit 1
        ;;
esac
