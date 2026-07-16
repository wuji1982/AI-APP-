const fs = require('fs');
const path = require('path');

const tabDir = path.join(__dirname, 'src', 'static', 'tab');

// 简单的 1x1 像素 PNG 作为占位图标
const placeholderPng = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
  'base64'
);

const icons = [
  'home.png', 'home-active.png',
  'mall.png', 'mall-active.png',
  'group.png', 'group-active.png',
  'message.png', 'message-active.png',
  'wallet.png', 'wallet-active.png',
  'mine.png', 'mine-active.png'
];

icons.forEach(name => {
  fs.writeFileSync(path.join(tabDir, name), placeholderPng);
  console.log('Created:', name);
});

console.log('All tab icons created!');
