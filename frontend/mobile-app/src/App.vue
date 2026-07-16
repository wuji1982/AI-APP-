<script>
export default {
  onLaunch() {
    console.log('AI共享商城 App Launch')
  },
  onShow() {
    console.log('App Show')
  },
  onHide() {
    console.log('App Hide')
  }
}
</script>

<style>
/* ===== 全局基础样式 ===== */
page {
  background-color: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
  font-size: 14px;
  color: #303133;
  line-height: 1.5;
  box-sizing: border-box;
}

*, *::before, *::after {
  box-sizing: border-box;
}

/* ===== 通用卡片 ===== */
.card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
}

/* ===== 通用按钮 ===== */
.btn-primary {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: #fff;
  border: none;
  border-radius: 22px;
  padding: 10px 0;
  font-size: 15px;
  font-weight: 500;
  text-align: center;
}

.btn-primary:active {
  opacity: 0.85;
}

.btn-outline {
  background: #fff;
  color: #409eff;
  border: 1px solid #409eff;
  border-radius: 22px;
  padding: 10px 0;
  font-size: 15px;
  text-align: center;
}

.btn-danger {
  background: linear-gradient(135deg, #f56c6c, #e74c3c);
  color: #fff;
  border: none;
  border-radius: 22px;
  padding: 10px 0;
  font-size: 15px;
  font-weight: 500;
  text-align: center;
}

.btn-disabled {
  background: #e0e0e0;
  color: #999;
  border: none;
  border-radius: 22px;
  padding: 10px 0;
  font-size: 15px;
  text-align: center;
}

/* ===== 空状态 ===== */
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-state .empty-icon {
  font-size: 50px;
  display: block;
  margin-bottom: 12px;
}

.empty-state .empty-text {
  font-size: 15px;
  color: #999;
  display: block;
  margin-bottom: 4px;
}

.empty-state .empty-hint {
  font-size: 13px;
  color: #ccc;
  display: block;
}

/* ===== 加载状态 ===== */
.loading-tip {
  text-align: center;
  padding: 15px;
  color: #ccc;
  font-size: 13px;
}

/* ===== 分割线 ===== */
.divider {
  height: 1px;
  background: #ebeef5;
  margin: 12px 0;
}

/* ===== 价格样式 ===== */
.price-text {
  color: #f56c6c;
  font-weight: bold;
}

.price-original {
  color: #ccc;
  text-decoration: line-through;
  font-size: 12px;
  margin-left: 6px;
}

/* ===== 标签 ===== */
.tag {
  display: inline-block;
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 3px;
  margin-right: 4px;
}

.tag-primary { background: #f0f9ff; color: #409eff; }
.tag-success { background: #f0fff4; color: #67c23a; }
.tag-warning { background: #fff7e6; color: #e6a23c; }
.tag-danger { background: #fff0f0; color: #f56c6c; }

/* ===== 页面容器 ===== */
.page-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: env(safe-area-inset-bottom);
}

/* ===== 底部安全区 ===== */
.safe-bottom {
  padding-bottom: calc(env(safe-area-inset-bottom) + 60px);
}

/* ===== 单行省略 ===== */
.ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ===== 多行省略 ===== */
.ellipsis-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ===== 导航栏通用 ===== */
.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
}

.nav-title {
  font-size: 17px;
  font-weight: 600;
}

/* ===== 弹窗遮罩 ===== */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  width: 80%;
  max-width: 360px;
}

.modal-title {
  font-size: 17px;
  font-weight: 600;
  text-align: center;
  display: block;
  margin-bottom: 16px;
}

/* ===== 徽章 ===== */
.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 16px;
  height: 16px;
  line-height: 16px;
  text-align: center;
  background: #f56c6c;
  color: #fff;
  font-size: 10px;
  border-radius: 8px;
  padding: 0 4px;
}
</style>
