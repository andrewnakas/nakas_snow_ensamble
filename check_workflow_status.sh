#!/bin/bash
# Quick script to check workflow status
# This helps monitor the forecast generation

echo "============================================"
echo "🔍 Snow Ensemble Workflow Status Checker"
echo "============================================"
echo ""
echo "📋 Repository: andrewnakas/nakas_snow_ensamble"
echo "🌿 Branch: claude/snow-ensemble-github-actions-015sZZdvXEYTnKE7oVxsv1o1"
echo ""
echo "To check workflow status:"
echo ""
echo "1. 🌐 View in browser:"
echo "   https://github.com/andrewnakas/nakas_snow_ensamble/actions"
echo ""
echo "2. 📊 Once complete, view your forecast:"
echo "   https://andrewnakas.github.io/nakas_snow_ensamble/"
echo ""
echo "3. ⏱️  Expected runtime: 10-15 minutes"
echo ""
echo "============================================"
echo "Workflow triggered by latest push at:"
git log -1 --format="%h - %s (%cr)" --date=relative
echo "============================================"
echo ""
