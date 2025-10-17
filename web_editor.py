import sys
import os
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QSplitter, QPushButton, QFileDialog, 
                            QAction, QToolBar, QMessageBox, QLabel, QStatusBar, 
                            QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
                            QComboBox, QLineEdit, QColorDialog, QMenu, QInputDialog, 
                            QFormLayout, QGridLayout, QCheckBox, QSlider, QGroupBox, 
                            QSpinBox, QDoubleSpinBox, QFrame, QDialog, QAbstractItemDelegate)
from PyQt5.QtCore import Qt, QUrl, QMimeData, QPoint, QSize
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import (QIcon, QColor, QFont, QTextCursor, QSyntaxHighlighter, 
                         QTextCharFormat, QDrag, QPainter, QBrush, QPen, QCursor, 
                         QLinearGradient, QPalette)

# 版本信息
VERSION = "v0.1.0"

# 定义界面颜色主题 - 现代化设计
class Theme:
    # 主色调
    BACKGROUND = QColor(30, 35, 40)
    SURFACE = QColor(40, 45, 50)
    SURFACE_LIGHT = QColor(45, 50, 55)
    SURFACE_DARK = QColor(35, 40, 45)
    
    # 强调色
    PRIMARY = QColor(100, 150, 230)
    PRIMARY_LIGHT = QColor(120, 170, 250)
    PRIMARY_DARK = QColor(80, 130, 210)
    SECONDARY = QColor(139, 233, 253)
    ACCENT = QColor(80, 250, 123)
    ACCENT_LIGHT = QColor(100, 255, 143)
    
    # 文本色
    TEXT = QColor(250, 250, 250)
    TEXT_SECONDARY = QColor(180, 185, 190)
    TEXT_DARK = QColor(150, 155, 160)
    
    # 状态色
    ERROR = QColor(255, 100, 100)
    SUCCESS = QColor(80, 250, 123)
    WARNING = QColor(255, 184, 108)
    INFO = QColor(66, 165, 245)
    
    # 边框和分隔线
    BORDER = QColor(50, 55, 60)
    DIVIDER = QColor(55, 60, 65)
    
    # 积木颜色 - 更鲜艳和区分度高
    BLOCK_HTML = QColor(255, 145, 0)
    BLOCK_CSS = QColor(134, 66, 244)
    BLOCK_JS = QColor(255, 223, 0)
    BLOCK_LAYOUT = QColor(66, 165, 245)
    BLOCK_STYLE = QColor(219, 76, 223)
    BLOCK_EVENT = QColor(255, 85, 85)
    BLOCK_ANIMATION = QColor(76, 175, 80)
    BLOCK_MEDIA = QColor(244, 67, 54)
    
    # 阴影和渐变
    SHADOW = "rgba(0, 0, 0, 0.2)"
    
    @staticmethod
    def get_gradient(color1, color2):
        gradient = QLinearGradient(0, 0, 1, 0)
        gradient.setColorAt(0, color1)
        gradient.setColorAt(1, color2)
        return gradient

# 自定义滚动区域，用于拖拽组件
class BlockItem(QListWidgetItem):
    def __init__(self, name, block_type, code_template, color, parameters=None, element_type=None, params=None, parent=None):
        super().__init__(name, parent)
        self.block_type = block_type
        self.code_template = code_template
        self.color = color
        self.parameters = parameters or []  # 参数定义列表
        self.parameter_values = {}  # 参数值
        self.element_type = element_type  # 元素类型，用于识别专用编辑器
        self.params = params or {}  # 扩展参数字典
        self.setSizeHint(QSize(200, 40))
        
        # 初始化参数默认值
        for param in self.parameters:
            self.parameter_values[param['name']] = param.get('default', '')
    
    def get_processed_code(self):
        """根据参数值处理代码模板"""
        code = self.code_template
        for param_name, value in self.parameter_values.items():
            code = code.replace(f"{{{{{param_name}}}}}", str(value))
        return code
    
    def update_parameter(self, param_name, value):
        """更新参数值"""
        if param_name in self.parameter_values:
            self.parameter_values[param_name] = value
            return True
        return False
    
    def get_parameter_editor(self):
        """获取参数编辑器窗口"""
        # 根据元素类型选择合适的编辑器
        if self.element_type and self.element_type.startswith('html_'):
            return HTMLElementEditor(self)
        elif self.element_type and self.element_type.startswith('css_'):
            return CSSStyleEditor(self)
        elif self.element_type and self.element_type.startswith('js_'):
            return JSInteractionEditor(self)
        return ParameterEditor(self)


class HTMLElementEditor(QDialog):
    """HTML元素专用编辑器"""
    def __init__(self, block_item, parent=None):
        super().__init__(parent)
        self.block_item = block_item
        self.setWindowTitle(f"编辑 {block_item.text()}")
        self.setModal(True)
        self.setStyleSheet(""
            "background-color: #2d2d2d; color: #ffffff;"
             "QLineEdit, QTextEdit, QComboBox { background-color: #3d3d3d; border: 1px solid #555; color: #ffffff; border-radius: 4px; padding: 6px; }"
             "QLabel { color: #ffffff; padding: 4px 0; }"
             "QPushButton { background-color: #4a9eff; color: white; border: none; border-radius: 4px; padding: 8px 16px; }"
            "QPushButton:hover { background-color: #6aa8ff; }"
            "QSpinBox, QDoubleSpinBox { background-color: #3d3d3d; color: #ffffff; border: 1px solid #555; border-radius: 4px; }")
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        params = self.block_item.params.copy()
        
        # 根据元素类型创建不同的编辑控件
        if self.block_item.element_type == 'html_h1':
            # 标题编辑器
            self.title_edit = QLineEdit(params.get('text', '标题文本'))
            layout.addWidget(QLabel("标题内容:"))
            layout.addWidget(self.title_edit)
            
            self.level_combo = QComboBox()
            self.level_combo.addItems(['1', '2', '3', '4', '5', '6'])
            self.level_combo.setCurrentText(params.get('level', '1'))
            layout.addWidget(QLabel("标题级别:"))
            layout.addWidget(self.level_combo)
            
            self.color_edit = QLineEdit(params.get('color', '#000000'))
            layout.addWidget(QLabel("标题颜色:"))
            layout.addWidget(self.color_edit)
        
        elif self.block_item.element_type == 'html_p':
            # 段落编辑器
            self.paragraph_edit = QTextEdit(params.get('text', '这是一个段落'))
            self.paragraph_edit.setMinimumHeight(80)
            layout.addWidget(QLabel("段落内容:"))
            layout.addWidget(self.paragraph_edit)
            
            self.color_edit = QLineEdit(params.get('color', '#000000'))
            layout.addWidget(QLabel("文字颜色:"))
            layout.addWidget(self.color_edit)
            
            self.align_combo = QComboBox()
            self.align_combo.addItems(['left', 'center', 'right', 'justify'])
            self.align_combo.setCurrentText(params.get('align', 'left'))
            layout.addWidget(QLabel("对齐方式:"))
            layout.addWidget(self.align_combo)
        
        elif self.block_item.element_type == 'html_button':
            # 按钮编辑器
            self.button_text_edit = QLineEdit(params.get('text', '点击我'))
            layout.addWidget(QLabel("按钮文字:"))
            layout.addWidget(self.button_text_edit)
            
            self.bgcolor_edit = QLineEdit(params.get('bgcolor', '#007bff'))
            layout.addWidget(QLabel("背景颜色:"))
            layout.addWidget(self.bgcolor_edit)
            
            self.color_edit = QLineEdit(params.get('color', '#ffffff'))
            layout.addWidget(QLabel("文字颜色:"))
            layout.addWidget(self.color_edit)
            
            self.size_combo = QComboBox()
            self.size_combo.addItems(['small', 'medium', 'large'])
            self.size_combo.setCurrentText(params.get('size', 'medium'))
            layout.addWidget(QLabel("按钮大小:"))
            layout.addWidget(self.size_combo)
        
        elif self.block_item.element_type == 'html_img':
            # 图片编辑器
            self.src_edit = QLineEdit(params.get('src', 'https://example.com/image.jpg'))
            layout.addWidget(QLabel("图片URL:"))
            layout.addWidget(self.src_edit)
            
            self.alt_edit = QLineEdit(params.get('alt', '图片描述'))
            layout.addWidget(QLabel("替代文本:"))
            layout.addWidget(self.alt_edit)
            
            self.width_edit = QLineEdit(params.get('width', '300'))
            layout.addWidget(QLabel("宽度:"))
            layout.addWidget(self.width_edit)
            
            self.height_edit = QLineEdit(params.get('height', ''))
            layout.addWidget(QLabel("高度:"))
            layout.addWidget(self.height_edit)
        
        elif self.block_item.element_type == 'html_a':
            # 链接编辑器
            self.href_edit = QLineEdit(params.get('href', 'https://example.com'))
            layout.addWidget(QLabel("链接URL:"))
            layout.addWidget(self.href_edit)
            
            self.text_edit = QLineEdit(params.get('text', '访问网站'))
            layout.addWidget(QLabel("链接文字:"))
            layout.addWidget(self.text_edit)
            
            self.target_combo = QComboBox()
            self.target_combo.addItems(['_self', '_blank', '_parent', '_top'])
            self.target_combo.setCurrentText(params.get('target', '_blank'))
            layout.addWidget(QLabel("打开方式:"))
            layout.addWidget(self.target_combo)
        
        elif self.block_item.element_type == 'html_div':
            # 容器编辑器
            self.class_edit = QLineEdit(params.get('class', 'container'))
            layout.addWidget(QLabel("CSS类名:"))
            layout.addWidget(self.class_edit)
            
            self.bgcolor_edit = QLineEdit(params.get('bgcolor', '#f8f9fa'))
            layout.addWidget(QLabel("背景颜色:"))
            layout.addWidget(self.bgcolor_edit)
            
            self.padding_edit = QLineEdit(params.get('padding', '20px'))
            layout.addWidget(QLabel("内边距:"))
            layout.addWidget(self.padding_edit)
        
        elif self.block_item.element_type == 'html_ul':
            # 列表编辑器
            self.list_type_combo = QComboBox()
            self.list_type_combo.addItems(['ul', 'ol'])
            self.list_type_combo.setCurrentText(params.get('type', 'ul'))
            layout.addWidget(QLabel("列表类型:"))
            layout.addWidget(self.list_type_combo)
            
            # 列表项编辑
            self.list_items = params.get('items', ['项目1', '项目2'])
            self.items_layout = QVBoxLayout()
            self.update_items_layout()
            
            button_layout = QHBoxLayout()
            add_button = QPushButton("添加项目")
            add_button.clicked.connect(self.add_list_item)
            button_layout.addWidget(add_button)
            
            layout.addLayout(self.items_layout)
            layout.addLayout(button_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.resize(400, 300)
    
    def update_items_layout(self):
        # 清除现有布局
        while self.items_layout.count() > 0:
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加列表项输入框
        for i, text in enumerate(self.list_items):
            item_layout = QHBoxLayout()
            item_edit = QLineEdit(text)
            item_edit.setObjectName(f"item_{i}")
            item_edit.textChanged.connect(lambda text, idx=i: self.update_item(idx, text))
            item_layout.addWidget(item_edit)
            
            remove_button = QPushButton("删除")
            remove_button.setObjectName(f"remove_{i}")
            remove_button.clicked.connect(lambda checked, idx=i: self.remove_list_item(idx))
            item_layout.addWidget(remove_button)
            
            self.items_layout.addLayout(item_layout)
    
    def add_list_item(self):
        self.list_items.append(f"项目{len(self.list_items) + 1}")
        self.update_items_layout()
    
    def remove_list_item(self, index):
        if 0 <= index < len(self.list_items):
            del self.list_items[index]
            self.update_items_layout()
    
    def update_item(self, index, text):
        if 0 <= index < len(self.list_items):
            self.list_items[index] = text
    
    def accept(self):
        # 保存参数
        params = {}
        
        if self.block_item.element_type == 'html_h1':
            params['text'] = self.title_edit.text()
            params['level'] = self.level_combo.currentText()
            params['color'] = self.color_edit.text()
            # 更新代码模板
            level = int(params['level'])
            self.block_item.code_template = f"<h{level} style='color: {params['color']};'>{params['text']}</h{level}>"
        
        elif self.block_item.element_type == 'html_p':
            params['text'] = self.paragraph_edit.toPlainText()
            params['color'] = self.color_edit.text()
            params['align'] = self.align_combo.currentText()
            self.block_item.code_template = f"<p style='color: {params['color']}; text-align: {params['align']};'>{params['text']}</p>"
        
        elif self.block_item.element_type == 'html_button':
            params['text'] = self.button_text_edit.text()
            params['bgcolor'] = self.bgcolor_edit.text()
            params['color'] = self.color_edit.text()
            params['size'] = self.size_combo.currentText()
            size_map = {'small': '12px', 'medium': '16px', 'large': '20px'}
            font_size = size_map.get(params['size'], '16px')
            self.block_item.code_template = f"<button style='background-color: {params['bgcolor']}; color: {params['color']}; font-size: {font_size}; padding: 8px 16px; border: none; border-radius: 4px;'>{params['text']}</button>"
        
        elif self.block_item.element_type == 'html_img':
            params['src'] = self.src_edit.text()
            params['alt'] = self.alt_edit.text()
            params['width'] = self.width_edit.text()
            params['height'] = self.height_edit.text()
            width_attr = f" width='{params['width']}'" if params['width'] else ''
            height_attr = f" height='{params['height']}'" if params['height'] else ''
            self.block_item.code_template = f"<img src='{params['src']}' alt='{params['alt']}'{width_attr}{height_attr}>"
        
        elif self.block_item.element_type == 'html_a':
            params['href'] = self.href_edit.text()
            params['text'] = self.text_edit.text()
            params['target'] = self.target_combo.currentText()
            self.block_item.code_template = f"<a href='{params['href']}' target='{params['target']}'>{params['text']}</a>"
        
        elif self.block_item.element_type == 'html_div':
            params['class'] = self.class_edit.text()
            params['bgcolor'] = self.bgcolor_edit.text()
            params['padding'] = self.padding_edit.text()
            self.block_item.code_template = f"<div class='{params['class']}' style='background-color: {params['bgcolor']}; padding: {params['padding']};'></div>"
        
        elif self.block_item.element_type == 'html_ul':
            params['items'] = self.list_items
            params['type'] = self.list_type_combo.currentText()
            tag = 'ul' if params['type'] == 'ul' else 'ol'
            items_html = '\n'.join([f"    <li>{item}</li>" for item in params['items']])
            self.block_item.code_template = f"<{tag}>\n{items_html}\n</{tag}>"
        
        self.block_item.params = params
        super().accept()


class CSSStyleEditor(QDialog):
    """CSS样式专用编辑器"""
    def __init__(self, block_item, parent=None):
        super().__init__(parent)
        self.block_item = block_item
        self.setWindowTitle(f"编辑样式 - {block_item.text()}")
        self.setModal(True)
        self.setStyleSheet(""
            "background-color: #2d2d2d; color: #ffffff;"
            "QLineEdit, QTextEdit, QComboBox { background-color: #3d3d3d; border: 1px solid #555; color: #ffffff; border-radius: 4px; padding: 6px; }"
            "QLabel { color: #ffffff; padding: 4px 0; }"
            "QPushButton { background-color: #4a9eff; color: white; border: none; border-radius: 4px; padding: 8px 16px; }"
            "QPushButton:hover { background-color: #6aa8ff; }"
            "QSpinBox, QDoubleSpinBox { background-color: #3d3d3d; color: #ffffff; border: 1px solid #555; border-radius: 4px; }")
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        params = self.block_item.params.copy()
        
        # 通用选择器输入
        self.selector_edit = QLineEdit(params.get('selector', 'body'))
        layout.addWidget(QLabel("CSS选择器:"))
        layout.addWidget(self.selector_edit)
        
        # 根据样式类型创建不同的编辑控件
        if self.block_item.element_type == 'css_bgcolor':
            # 背景色编辑器
            self.color_edit = QLineEdit(params.get('color', '#ffffff'))
            layout.addWidget(QLabel("背景颜色:"))
            layout.addWidget(self.color_edit)
        
        elif self.block_item.element_type == 'css_textcolor':
            # 文字颜色编辑器
            self.color_edit = QLineEdit(params.get('color', '#000000'))
            layout.addWidget(QLabel("文字颜色:"))
            layout.addWidget(self.color_edit)
        
        elif self.block_item.element_type == 'css_fontsize':
            # 字体大小编辑器
            self.size_spin = QSpinBox()
            self.size_spin.setRange(8, 72)
            self.size_spin.setValue(int(params.get('size', '16')))
            layout.addWidget(QLabel("字体大小 (px):"))
            layout.addWidget(self.size_spin)
        
        elif self.block_item.element_type == 'css_margin':
            # 边距编辑器
            margin_layout = QGridLayout()
            margin_layout.addWidget(QLabel("上边距:"), 0, 0)
            margin_layout.addWidget(QLabel("右边距:"), 0, 1)
            margin_layout.addWidget(QLabel("下边距:"), 1, 0)
            margin_layout.addWidget(QLabel("左边距:"), 1, 1)
            
            self.margin_top = QSpinBox()
            self.margin_top.setRange(0, 100)
            self.margin_top.setValue(int(params.get('top', '10')))
            margin_layout.addWidget(self.margin_top, 0, 2)
            
            self.margin_right = QSpinBox()
            self.margin_right.setRange(0, 100)
            self.margin_right.setValue(int(params.get('right', '10')))
            margin_layout.addWidget(self.margin_right, 0, 3)
            
            self.margin_bottom = QSpinBox()
            self.margin_bottom.setRange(0, 100)
            self.margin_bottom.setValue(int(params.get('bottom', '10')))
            margin_layout.addWidget(self.margin_bottom, 1, 2)
            
            self.margin_left = QSpinBox()
            self.margin_left.setRange(0, 100)
            self.margin_left.setValue(int(params.get('left', '10')))
            margin_layout.addWidget(self.margin_left, 1, 3)
            
            layout.addLayout(margin_layout)
        
        elif self.block_item.element_type == 'css_shadow':
            # 阴影编辑器
            shadow_layout = QGridLayout()
            shadow_layout.addWidget(QLabel("水平偏移:"), 0, 0)
            shadow_layout.addWidget(QLabel("垂直偏移:"), 1, 0)
            shadow_layout.addWidget(QLabel("模糊半径:"), 2, 0)
            shadow_layout.addWidget(QLabel("阴影颜色:"), 3, 0)
            
            self.shadow_horizontal = QSpinBox()
            self.shadow_horizontal.setRange(-50, 50)
            self.shadow_horizontal.setValue(int(params.get('horizontal', '0')))
            shadow_layout.addWidget(self.shadow_horizontal, 0, 1)
            
            self.shadow_vertical = QSpinBox()
            self.shadow_vertical.setRange(-50, 50)
            self.shadow_vertical.setValue(int(params.get('vertical', '4')))
            shadow_layout.addWidget(self.shadow_vertical, 1, 1)
            
            self.shadow_blur = QSpinBox()
            self.shadow_blur.setRange(0, 100)
            self.shadow_blur.setValue(int(params.get('blur', '8')))
            shadow_layout.addWidget(self.shadow_blur, 2, 1)
            
            self.shadow_color = QLineEdit(params.get('color', 'rgba(0,0,0,0.1)'))
            shadow_layout.addWidget(self.shadow_color, 3, 1)
            
            layout.addLayout(shadow_layout)
        
        elif self.block_item.element_type == 'css_borderradius':
            # 圆角编辑器
            self.radius_spin = QSpinBox()
            self.radius_spin.setRange(0, 100)
            self.radius_spin.setValue(int(params.get('radius', '8')))
            layout.addWidget(QLabel("圆角半径 (px):"))
            layout.addWidget(self.radius_spin)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.resize(400, 250)
    
    def accept(self):
        # 保存参数并更新代码模板
        params = {'selector': self.selector_edit.text()}
        selector = params['selector']
        
        if self.block_item.element_type == 'css_bgcolor':
            params['color'] = self.color_edit.text()
            self.block_item.code_template = f"{selector} {{ background-color: {params['color']}; }}"
        
        elif self.block_item.element_type == 'css_textcolor':
            params['color'] = self.color_edit.text()
            self.block_item.code_template = f"{selector} {{ color: {params['color']}; }}"
        
        elif self.block_item.element_type == 'css_fontsize':
            params['size'] = str(self.size_spin.value())
            self.block_item.code_template = f"{selector} {{ font-size: {params['size']}px; }}"
        
        elif self.block_item.element_type == 'css_margin':
            params['top'] = str(self.margin_top.value())
            params['right'] = str(self.margin_right.value())
            params['bottom'] = str(self.margin_bottom.value())
            params['left'] = str(self.margin_left.value())
            self.block_item.code_template = f"{selector} {{ margin: {params['top']}px {params['right']}px {params['bottom']}px {params['left']}px; }}"
        
        elif self.block_item.element_type == 'css_shadow':
            params['horizontal'] = str(self.shadow_horizontal.value())
            params['vertical'] = str(self.shadow_vertical.value())
            params['blur'] = str(self.shadow_blur.value())
            params['color'] = self.shadow_color.text()
            self.block_item.code_template = f"{selector} {{ box-shadow: {params['horizontal']}px {params['vertical']}px {params['blur']}px {params['color']}; }}"
        
        elif self.block_item.element_type == 'css_borderradius':
            params['radius'] = str(self.radius_spin.value())
            self.block_item.code_template = f"{selector} {{ border-radius: {params['radius']}px; }}"
        
        self.block_item.params = params
        super().accept()


class JSInteractionEditor(QDialog):
    """JavaScript交互专用编辑器"""
    def __init__(self, block_item, parent=None):
        super().__init__(parent)
        self.block_item = block_item
        self.setWindowTitle(f"编辑交互 - {block_item.text()}")
        self.setModal(True)
        self.setStyleSheet(""
            "background-color: #2d2d2d; color: #ffffff;"
            "QLineEdit, QTextEdit, QComboBox { background-color: #3d3d3d; border: 1px solid #555; color: #ffffff; border-radius: 4px; padding: 6px; }"
            "QLabel { color: #ffffff; padding: 4px 0; }"
            "QPushButton { background-color: #4a9eff; color: white; border: none; border-radius: 4px; padding: 8px 16px; }"
            "QPushButton:hover { background-color: #6aa8ff; }"
            "QPlainTextEdit { background-color: #3d3d3d; color: #ffffff; border: 1px solid #555; border-radius: 4px; }"
            "QTextEdit { min-height: 80px; }"
        )
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        params = self.block_item.params.copy()
        
        # 根据交互类型创建不同的编辑控件
        if self.block_item.element_type in ['js_click', 'js_mouseover', 'js_textcontent', 'js_addclass', 'js_hide', 'js_show']:
            # 选择器输入
            self.selector_edit = QLineEdit(params.get('selector', 'button'))
            layout.addWidget(QLabel("元素选择器:"))
            layout.addWidget(self.selector_edit)
        
        if self.block_item.element_type == 'js_click' or self.block_item.element_type == 'js_mouseover':
            # 动作编辑器
            self.action_edit = QTextEdit(params.get('action', 'alert("交互成功!")'))
            self.action_edit.setMinimumHeight(100)
            layout.addWidget(QLabel("JavaScript动作:"))
            layout.addWidget(self.action_edit)
            
            # 预设动作按钮
            preset_layout = QHBoxLayout()
            preset_label = QLabel("快速预设:")
            alert_btn = QPushButton("提示框")
            alert_btn.clicked.connect(lambda: self.set_preset("alert(\"操作成功!\");"))
            change_color_btn = QPushButton("变色")
            change_color_btn.clicked.connect(lambda: self.set_preset("this.style.backgroundColor = '#ff6b6b';"))
            toggle_btn = QPushButton("显示/隐藏")
            toggle_btn.clicked.connect(lambda: self.set_preset("this.style.display = this.style.display === 'none' ? 'block' : 'none';"))
            
            preset_layout.addWidget(preset_label)
            preset_layout.addWidget(alert_btn)
            preset_layout.addWidget(change_color_btn)
            preset_layout.addWidget(toggle_btn)
            preset_layout.addStretch()
            layout.addLayout(preset_layout)
        
        elif self.block_item.element_type == 'js_alert':
            # 提示框编辑器
            self.message_edit = QLineEdit(params.get('message', '提示信息'))
            layout.addWidget(QLabel("提示内容:"))
            layout.addWidget(self.message_edit)
        
        elif self.block_item.element_type == 'js_textcontent':
            # 内容修改编辑器
            self.text_edit = QLineEdit(params.get('text', '新内容'))
            layout.addWidget(QLabel("新的文本内容:"))
            layout.addWidget(self.text_edit)
        
        elif self.block_item.element_type == 'js_addclass':
            # 添加类编辑器
            self.class_edit = QLineEdit(params.get('class', 'active'))
            layout.addWidget(QLabel("CSS类名:"))
            layout.addWidget(self.class_edit)
        
        elif self.block_item.element_type == 'js_show':
            # 显示方式编辑器
            self.display_combo = QComboBox()
            self.display_combo.addItems(['block', 'inline', 'inline-block', 'flex', 'grid'])
            self.display_combo.setCurrentText(params.get('display', 'block'))
            layout.addWidget(QLabel("显示方式:"))
            layout.addWidget(self.display_combo)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.resize(500, 300)
    
    def set_preset(self, code):
        """设置预设代码"""
        self.action_edit.setPlainText(code)
    
    def accept(self):
        # 保存参数并更新代码模板
        params = {}
        
        if self.block_item.element_type == 'js_click':
            params['selector'] = self.selector_edit.text()
            params['action'] = self.action_edit.toPlainText()
            self.block_item.code_template = f"document.querySelector('{params['selector']}').addEventListener('click', function() {{\n    {params['action']}\n}});"
        
        elif self.block_item.element_type == 'js_mouseover':
            params['selector'] = self.selector_edit.text()
            params['action'] = self.action_edit.toPlainText()
            self.block_item.code_template = f"document.querySelector('{params['selector']}').addEventListener('mouseover', function() {{\n    {params['action']}\n}});"
        
        elif self.block_item.element_type == 'js_alert':
            params['message'] = self.message_edit.text()
            self.block_item.code_template = f"alert('{params['message']}');"
        
        elif self.block_item.element_type == 'js_textcontent':
            params['selector'] = self.selector_edit.text()
            params['text'] = self.text_edit.text()
            self.block_item.code_template = f"document.querySelector('{params['selector']}').textContent = '{params['text']}';"
        
        elif self.block_item.element_type == 'js_addclass':
            params['selector'] = self.selector_edit.text()
            params['class'] = self.class_edit.text()
            self.block_item.code_template = f"document.querySelector('{params['selector']}').classList.add('{params['class']}');"
        
        elif self.block_item.element_type == 'js_hide':
            params['selector'] = self.selector_edit.text()
            self.block_item.code_template = f"document.querySelector('{params['selector']}').style.display = 'none';"
        
        elif self.block_item.element_type == 'js_show':
            params['selector'] = self.selector_edit.text()
            params['display'] = self.display_combo.currentText()
            self.block_item.code_template = f"document.querySelector('{params['selector']}').style.display = '{params['display']}';"
        
        self.block_item.params = params
        super().accept()

# 参数编辑器 - 根据参数类型显示不同的输入控件
class ParameterEditor(QWidget):
    def __init__(self, block_item):
        super().__init__()
        self.block_item = block_item
        self.setWindowTitle(f"编辑 {block_item.text()} 参数")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("""
            QWidget { background-color: #f5f5f5; color: #333333; }
            QLabel { color: #666666; font-size: 14px; }
            QPushButton { background-color: #4a90e2; color: white; border: none; padding: 8px 16px; border-radius: 4px; }
            QPushButton:hover { background-color: #5b9cf2; }
            QPushButton:pressed { background-color: #3a80d2; }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background-color: #ffffff; color: #333333; border: 1px solid #cccccc; border-radius: 4px; padding: 6px; }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus { border-color: #4a90e2; }
            QGroupBox { border: 1px solid #cccccc; border-radius: 6px; margin-top: 10px; padding: 10px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; color: #666666; font-weight: bold; }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建参数编辑表单
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # 存储创建的控件引用
        self.controls = {}
        
        # 为每个参数创建合适的输入控件
        for param in self.block_item.parameters:
            param_name = param['name']
            param_type = param['type']
            param_label = QLabel(f"{param.get('label', param_name)}")
            
            # 根据参数类型创建不同的控件
            if param_type == 'string':
                control = QLineEdit(self.block_item.parameter_values.get(param_name, ''))
                if param.get('placeholder'):
                    control.setPlaceholderText(param['placeholder'])
            
            elif param_type == 'number':
                min_val = param.get('min', 0)
                max_val = param.get('max', 100)
                step = param.get('step', 1)
                decimals = param.get('decimals', 0)
                
                if decimals > 0:
                    control = QDoubleSpinBox()
                    control.setDecimals(decimals)
                    control.setSingleStep(step)
                else:
                    control = QSpinBox()
                    control.setSingleStep(step)
                
                control.setMinimum(min_val)
                control.setMaximum(max_val)
                control.setValue(float(self.block_item.parameter_values.get(param_name, min_val)))
            
            elif param_type == 'select':
                control = QComboBox()
                options = param.get('options', [])
                for option in options:
                    if isinstance(option, tuple):
                        control.addItem(option[1], option[0])
                    else:
                        control.addItem(option)
                
                # 设置当前值
                current_val = self.block_item.parameter_values.get(param_name, '')
                index = control.findData(current_val)
                if index >= 0:
                    control.setCurrentIndex(index)
                elif current_val in [control.itemText(i) for i in range(control.count())]:
                    control.setCurrentText(current_val)
            
            elif param_type == 'color':
                control_layout = QHBoxLayout()
                color_button = QPushButton()
                color_button.setFixedWidth(40)
                color_button.setFixedHeight(30)
                
                # 设置当前颜色
                current_color = self.block_item.parameter_values.get(param_name, '#FFFFFF')
                color_button.setStyleSheet(f"background-color: {current_color};")
                
                # 创建颜色预览文本
                color_text = QLineEdit(current_color)
                color_text.setReadOnly(True)
                
                # 连接颜色选择信号
                color_button.clicked.connect(lambda checked, c=color_text: self.select_color(c))
                
                control_layout.addWidget(color_button)
                control_layout.addWidget(color_text)
                control_layout.addStretch()
                
                # 存储控件引用
                self.controls[param_name] = (color_button, color_text)
                form_layout.setWidget(form_layout.rowCount(), QFormLayout.LabelRole, param_label)
                form_layout.setLayout(form_layout.rowCount() - 1, QFormLayout.FieldRole, control_layout)
                continue
            
            elif param_type == 'checkbox':
                control = QCheckBox()
                control.setChecked(self.block_item.parameter_values.get(param_name, False))
                form_layout.setWidget(form_layout.rowCount(), QFormLayout.LabelRole, param_label)
                form_layout.setWidget(form_layout.rowCount() - 1, QFormLayout.FieldRole, control)
                self.controls[param_name] = control
                continue
            
            elif param_type == 'slider':
                control_layout = QVBoxLayout()
                slider = QSlider(Qt.Horizontal)
                slider.setMinimum(param.get('min', 0))
                slider.setMaximum(param.get('max', 100))
                slider.setValue(int(self.block_item.parameter_values.get(param_name, 0)))
                
                value_label = QLabel(str(slider.value()))
                slider.valueChanged.connect(lambda value, label=value_label: label.setText(str(value)))
                
                control_layout.addWidget(slider)
                control_layout.addWidget(value_label, 0, Qt.AlignCenter)
                
                form_layout.setWidget(form_layout.rowCount(), QFormLayout.LabelRole, param_label)
                form_layout.setLayout(form_layout.rowCount() - 1, QFormLayout.FieldRole, control_layout)
                self.controls[param_name] = slider
                continue
            
            # 添加其他类型的控件...
            else:
                control = QLineEdit(str(self.block_item.parameter_values.get(param_name, '')))
            
            # 存储控件引用
            self.controls[param_name] = control
            form_layout.addRow(param_label, control)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"background-color: {Theme.DIVIDER.name()};")
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.close)
        
        apply_btn = QPushButton("应用")
        apply_btn.setStyleSheet(f"background-color: {Theme.ACCENT.name()}; color: black; font-weight: bold;")
        apply_btn.clicked.connect(self.apply_changes)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(apply_btn)
        
        # 添加到主布局
        layout.addLayout(form_layout)
        layout.addWidget(separator)
        layout.addLayout(button_layout)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.setLayout(layout)
    
    def select_color(self, color_text):
        current_color = color_text.text()
        try:
            initial = QColor(current_color)
        except:
            initial = QColor("#FFFFFF")
        
        color = QColorDialog.getColor(initial, self, "选择颜色")
        if color.isValid():
            color_str = color.name()
            color_text.setText(color_str)
            
            # 更新颜色按钮样式
            for param_name, controls in self.controls.items():
                if isinstance(controls, tuple) and len(controls) == 2 and controls[1] == color_text:
                    controls[0].setStyleSheet(f"background-color: {color_str};")
    
    def apply_changes(self):
        """应用所有参数更改"""
        for param in self.block_item.parameters:
            param_name = param['name']
            param_type = param['type']
            
            if param_name in self.controls:
                control = self.controls[param_name]
                
                # 根据控件类型获取值
                if isinstance(control, QLineEdit):
                    value = control.text()
                elif isinstance(control, QSpinBox):
                    value = control.value()
                elif isinstance(control, QDoubleSpinBox):
                    value = control.value()
                elif isinstance(control, QComboBox):
                    # 尝试获取数据，如果不存在则使用文本
                    value = control.currentData()
                    if value is None:
                        value = control.currentText()
                elif isinstance(control, QCheckBox):
                    value = control.isChecked()
                elif isinstance(control, QSlider):
                    value = control.value()
                elif isinstance(control, tuple) and len(control) == 2:  # 颜色控件
                    value = control[1].text()  # 从文本框获取颜色值
                else:
                    value = str(control)
                
                # 更新参数值
                self.block_item.update_parameter(param_name, value)
        
        # 关闭窗口
        self.close()

class BlockPalette(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setViewMode(QListWidget.ListMode)
        self.setSpacing(8)
        self.setStyleSheet("background-color: #f5f5f5; " + \
                            "color: #333333; " + \
                            "font-size: 14px; " + \
                            "padding: 10px; ")
        
    def startDrag(self, actions):
        item = self.currentItem()
        if item:
            # 创建新的积木实例，避免修改原始模板
            # 手动创建新实例而不是使用深拷贝，因为QListWidgetItem不可pickle
            new_item = BlockItem(
                name=item.text(),
                block_type=item.block_type,
                code_template=item.code_template,
                color=item.color,
                parameters=getattr(item, 'parameters', None),
                element_type=getattr(item, 'element_type', None),
                params=getattr(item, 'params', None)
            )
            
            # 将参数信息也序列化
            params_str = "|"
            if hasattr(item, 'parameters'):
                # 将参数定义转换为可序列化的格式
                import json
                params_str = "|" + json.dumps(item.parameters)
            
            mime_data = QMimeData()
            mime_data.setText(f"{item.block_type}:{item.text()}:{item.code_template}{params_str}")
            
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            
            # 创建拖拽时的视觉效果
            result = drag.exec_(Qt.CopyAction)
            
    def add_block(self, name, block_type, code_template, color, parameters=None):
        """添加一个积木项到面板"""
        item = BlockItem(name, block_type, code_template, color, parameters)
        # 设置积木的样式
        self.set_item_style(item)
        self.addItem(item)
    
    def set_item_style(self, item):
        """设置积木项的视觉样式"""
        # 这里可以自定义渲染，但Qt的QListWidgetItem样式有限
        # 实际渲染将在BlockEditor中实现

class BlockEditor(QListWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window  # 保存对主窗口的引用
        self.setAcceptDrops(True)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setSpacing(10)
        self.setStyleSheet("background-color: #f0f0f0; " + \
                            "color: #333333; " + \
                            "border: 2px dashed #4a9eff; " + \
                          "border-radius: 8px; " + \
                          "font-size: 14px; " + \
                          "padding: 15px; " + \
                          "min-height: 400px; ")
        
        # 启用自定义项目绘制
        self.setItemDelegate(BlockItemDelegate())
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        if event.mimeData().hasText():
            # 处理拖放的数据
            data = event.mimeData().text().split("|", 1)
            
            # 解析基本信息
            basic_info = data[0].split(":", 2)
            if len(basic_info) < 3:
                return
                
            block_type, name, code_template = basic_info
            parameters = []
            
            # 解析参数信息
            if len(data) > 1:
                try:
                    import json
                    parameters = json.loads(data[1])
                except:
                    pass
            
            # 根据类型选择颜色 - 使用新的主题颜色
            color_map = {
                "html": Theme.BLOCK_HTML,
                "css": Theme.BLOCK_CSS,
                "js": Theme.BLOCK_JS,
                "layout": Theme.BLOCK_LAYOUT,
                "style": Theme.BLOCK_STYLE,
                "event": Theme.BLOCK_EVENT,
                "animation": Theme.BLOCK_ANIMATION,
                "media": Theme.BLOCK_MEDIA
            }
            color = color_map.get(block_type, Theme.BLOCK_LAYOUT)
            
            # 创建新的积木项
            item = BlockItem(name, block_type, code_template, color, parameters)
            self.addItem(item)
            
            # 自动显示参数编辑窗口（如果有参数）
            if parameters:
                self.edit_item_parameters()
            
            # 更新代码
            if self.main_window:
                self.main_window.update_code_from_blocks()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            item = self.itemAt(event.pos())
            if item:
                self.setCurrentItem(item)
                self.show_context_menu(event.globalPos())
        elif event.button() == Qt.LeftButton and event.modifiers() == Qt.ControlModifier:
            # Ctrl+点击编辑元素
            item = self.itemAt(event.pos())
            if item:
                self.setCurrentItem(item)
                self.edit_item_parameters()
        super().mousePressEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        # 双击编辑元素
        item = self.itemAt(event.pos())
        if item:
            self.setCurrentItem(item)
            self.edit_item_parameters()
        super().mouseDoubleClickEvent(event)
    
    def show_context_menu(self, pos):
        menu = QMenu()
        menu.setStyleSheet("QMenu { background-color: " + Theme.SURFACE_LIGHT.name() + "; color: " + Theme.TEXT.name() + "; border: 1px solid " + Theme.BORDER.name() + "; } " + \
                          "QMenu::item { padding: 6px 30px; } " + \
                          "QMenu::item:selected { background-color: " + Theme.PRIMARY.name() + "; color: white; } ")
        
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(self.delete_selected_item)
        
        edit_action = QAction("编辑元素", self)
        # 有参数列表或元素类型属性就启用编辑选项
        item = self.currentItem()
        if hasattr(item, 'parameters') and item.parameters or hasattr(item, 'element_type'):
            edit_action.triggered.connect(self.edit_item_parameters)
        else:
            edit_action.setEnabled(False)
        
        duplicate_action = QAction("复制", self)
        duplicate_action.triggered.connect(self.duplicate_selected_item)
        
        menu.addAction(edit_action)
        menu.addAction(duplicate_action)
        menu.addSeparator()
        menu.addAction(delete_action)
        menu.exec_(pos)
    
    def delete_selected_item(self):
        item = self.currentItem()
        if item:
            # 获取元素名称（如果有）
            element_name = item.text()
            # 显示删除确认对话框
            reply = QMessageBox.question(
                self,
                '确认删除',
                f'确定要删除「{element_name}」吗？',
                QMessageBox.Yes | QMessageBox.No,
                  QMessageBox.No  # 默认选项为No
              )

            
            if reply == QMessageBox.Yes:
                index = self.row(item)
                self.takeItem(index)
                if self.main_window:
                    self.main_window.update_code_from_blocks()
    
    def duplicate_selected_item(self):
        item = self.currentItem()
        if item:
            import copy
            # 创建副本
            new_item = copy.deepcopy(item)
            # 添加到列表
            self.addItem(new_item)
            if self.main_window:
                self.main_window.update_code_from_blocks()
    
    def edit_item_parameters(self):
        item = self.currentItem()
        if item and (hasattr(item, 'parameters') and item.parameters or hasattr(item, 'element_type')):
            # 使用新的参数编辑器
            editor = item.get_parameter_editor()
            editor.setWindowModality(Qt.ApplicationModal)
            editor.show()
            
            # 连接关闭信号到代码更新
            editor.destroyed.connect(self._on_editor_closed)
    
    def _on_editor_closed(self):
        """当参数编辑器关闭时更新代码"""
        if self.main_window:
            self.main_window.update_code_from_blocks()

# 自定义积木项渲染委托
class BlockItemDelegate(QAbstractItemDelegate):
    def paint(self, painter, option, index):
        # 从模型中获取数据
        # 对于QListWidget，我们可以通过直接获取QListWidgetItem来访问BlockItem
        list_widget = option.styleObject
        if list_widget and hasattr(list_widget, 'item'):
            item = list_widget.item(index.row())
            if not isinstance(item, BlockItem):
                # 使用默认绘制
                painter.save()
                painter.fillRect(option.rect, option.palette.base())
                painter.drawText(option.rect, Qt.AlignCenter, index.data(Qt.DisplayRole))
                painter.restore()
                return
        else:
            # 如果无法获取item，使用默认绘制
            painter.save()
            painter.fillRect(option.rect, option.palette.base())
            painter.drawText(option.rect, Qt.AlignCenter, index.data(Qt.DisplayRole))
            painter.restore()
            return
        
        # 设置绘制区域
        rect = option.rect
        
        # 绘制背景
        painter.save()
        
        # 设置渐变背景
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        gradient.setColorAt(0, item.color.lighter(110))
        gradient.setColorAt(1, item.color)
        
        painter.fillRect(rect, gradient)
        
        # 绘制边框
        painter.setPen(QPen(item.color.darker(150), 2))
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 8, 8)
        
        # 绘制文本
        painter.setPen(QPen(Theme.TEXT))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, item.text())
        
        # 如果有参数，显示提示
        if hasattr(item, 'parameters') and item.parameters:
            param_count = len(item.parameters)
            painter.setFont(QFont("Arial", 9))
            painter.setPen(QPen(Theme.TEXT_SECONDARY))
            painter.drawText(rect.right() - 20, rect.bottom() - 5, str(param_count))
        
        painter.restore()
    
    def sizeHint(self, option, index):
        # 返回默认大小
        return QSize(200, 40)

class CodeEditor(QTextEdit):
    def __init__(self, language="html", parent=None):
        super().__init__(parent)
        self.language = language
        self.setTabStopWidth(40)
        self.setFont(QFont("Consolas", 12))
        self.setStyleSheet("background-color: #ffffff; " + \
                            "color: #333333; " + \
                            "border: 1px solid #cccccc; " + \
                            "border-radius: 6px; " + \
                            "padding: 15px; " + \
                          "selection-background-color: " + Theme.PRIMARY_DARK.name() + "; ")
        self.setAcceptRichText(False)
        self.setUndoRedoEnabled(True)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        
        # 启用语法高亮
        if language == "html":
            self.highlighter = HTMLHighlighter(self.document())
        elif language == "css":
            self.highlighter = CSSHighlighter(self.document())
        elif language == "js":
            self.highlighter = JavaScriptHighlighter(self.document())

# 基础语法高亮器
class BaseHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []
        
        # 字符串格式
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(Theme.SUCCESS)
        
        # 注释格式
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(Theme.TEXT_DARK)
        self.comment_format.setFontItalic(True)
        
    def highlightBlock(self, text):
        # 应用所有高亮规则
        for pattern, format in self.highlighting_rules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)
        
        # 处理多行注释和字符串
        self.setCurrentBlockState(0)

# HTML语法高亮器
class HTMLHighlighter(BaseHighlighter):
    def __init__(self, document):
        super().__init__(document)
        
        # HTML标签格式
        tag_format = QTextCharFormat()
        tag_format.setForeground(Theme.PRIMARY_LIGHT)
        tag_format.setFontWeight(QFont.Bold)
        
        # HTML属性格式
        attr_format = QTextCharFormat()
        attr_format.setForeground(Theme.SECONDARY)
        
        # HTML关键词
        keywords = ['html', 'head', 'body', 'title', 'meta', 'link', 'script',
                   'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                   'a', 'img', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th',
                   'form', 'input', 'button', 'select', 'option', 'textarea']
        
        # 添加标签规则
        for keyword in keywords:
            pattern = f'</?{keyword}\b[^>]*>'
            self.highlighting_rules.append((pattern, tag_format))
        
        # 添加属性规则
        self.highlighting_rules.append((r'\b\w+\s*=', attr_format))
        
        # 字符串规则
        self.highlighting_rules.append((r'"[^"]*"', self.string_format))
        self.highlighting_rules.append((r"'[^']*'", self.string_format))

# CSS语法高亮器
class CSSHighlighter(BaseHighlighter):
    def __init__(self, document):
        super().__init__(document)
        
        # CSS选择器格式
        selector_format = QTextCharFormat()
        selector_format.setForeground(Theme.BLOCK_CSS)
        selector_format.setFontWeight(QFont.Bold)
        
        # CSS属性格式
        property_format = QTextCharFormat()
        property_format.setForeground(Theme.SECONDARY)
        
        # CSS值格式
        value_format = QTextCharFormat()
        value_format.setForeground(Theme.TEXT_SECONDARY)
        
        # CSS关键词
        properties = ['color', 'background', 'font-size', 'font-family',
                     'margin', 'padding', 'border', 'display', 'position',
                     'width', 'height', 'flex', 'grid', 'align', 'justify',
                     'text-align', 'text-decoration']
        
        # 添加选择器规则
        self.highlighting_rules.append((r'[^@\s{][^{]*?(?=\s*\{)', selector_format))
        
        # 添加属性规则
        for prop in properties:
            self.highlighting_rules.append((fr'\b{prop}\b\s*:', property_format))
        
        # 添加值规则（颜色）
        self.highlighting_rules.append((r'#[0-9a-fA-F]{3,6}', value_format))
        
        # 添加值规则（单位）
        self.highlighting_rules.append((r'\b\d+\.?\d*\s*(px|em|rem|%|vh|vw)\b', value_format))
        
        # 字符串规则
        self.highlighting_rules.append((r'"[^"]*"', self.string_format))
        self.highlighting_rules.append((r"'[^']*'", self.string_format))
        
        # 注释规则
        self.highlighting_rules.append((r'\/\*.*?\*\/', self.comment_format))

# JavaScript语法高亮器
class JavaScriptHighlighter(BaseHighlighter):
    def __init__(self, document):
        super().__init__(document)
        
        # 关键字格式
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(Theme.BLOCK_JS)
        keyword_format.setFontWeight(QFont.Bold)
        
        # 函数名格式
        function_format = QTextCharFormat()
        function_format.setForeground(Theme.ACCENT)
        function_format.setFontWeight(QFont.Bold)
        
        # JavaScript关键词
        keywords = ['var', 'let', 'const', 'function', 'if', 'else', 'for', 'while',
                   'do', 'switch', 'case', 'default', 'return', 'break', 'continue',
                   'class', 'extends', 'import', 'export', 'from', 'async', 'await',
                   'new', 'this', 'true', 'false', 'null', 'undefined', 'typeof',
                   'instanceof', 'in', 'of', 'try', 'catch', 'finally', 'throw']
        
        # 添加关键字规则
        for keyword in keywords:
            self.highlighting_rules.append((fr'\b{keyword}\b', keyword_format))
        
        # 添加函数规则
        self.highlighting_rules.append((r'\b\w+(?=\s*\()', function_format))
        
        # 数字规则
        number_format = QTextCharFormat()
        number_format.setForeground(Theme.WARNING)
        self.highlighting_rules.append((r'\b\d+\.?\d*\b', number_format))
        
        # 字符串规则
        self.highlighting_rules.append((r'"[^"]*"', self.string_format))
        self.highlighting_rules.append((r"'[^']*'", self.string_format))
        self.highlighting_rules.append((r'`[^`]*`', self.string_format))
        
        # 注释规则
        self.highlighting_rules.append((r'\/\/.*$', self.comment_format))
        self.highlighting_rules.append((r'\/\*.*?\*\/', self.comment_format))

class ScratchWebEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.initUI()
        

        def __init__(self, element_type, parent=None):
            super().__init__(parent)
            self.setWindowTitle(f'编辑{element_type}元素')
            self.resize(400, 300)
            self.element_type = element_type
            self.result = None
            self.setup_ui()
        
        def setup_ui(self):
            layout = QVBoxLayout(self)
            self.setStyleSheet("""
                QDialog { background-color: #f0f0f0; }
                QLabel { color: #333333; font-weight: bold; margin-top: 10px; }
                QLineEdit, QTextEdit, QComboBox { 
                    background-color: #ffffff; 
                    color: #333333; 
                          border: 1px solid #cccccc; 
                          border-radius: 4px; 
                          padding: 8px; 
                      margin-bottom: 10px; 
                }
                QPushButton { 
                    background-color: #4a90e2; 
                      color: #ffffff; 
                      border: none; 
                      border-radius: 4px; 
                      padding: 8px 16px; 
                    font-weight: bold; 
                }
            """)
                    
                    
                    




            
            form_layout = QFormLayout()
            
            # 根据元素类型设置不同的输入字段
            if self.element_type == "标题":
                # 标题文本
                self.text_input = QLineEdit()
                self.text_input.setPlaceholderText("输入标题文本")
                form_layout.addRow("标题文本:", self.text_input)
                
                # 标题级别
                self.level_combo = QComboBox()
                self.level_combo.addItems(["h1 (最大)", "h2", "h3", "h4", "h5", "h6 (最小)"])
                form_layout.addRow("标题级别:", self.level_combo)
                
                # ID属性
                self.id_input = QLineEdit()
                self.id_input.setPlaceholderText("可选: 元素ID")
                form_layout.addRow("ID:", self.id_input)
                
                # 类属性
                self.class_input = QLineEdit()
                self.class_input.setPlaceholderText("可选: CSS类名")
                form_layout.addRow("CSS类:", self.class_input)
                
            elif self.element_type == "段落":
                # 段落文本
                self.text_input = QTextEdit()
                self.text_input.setPlaceholderText("输入段落内容")
                self.text_input.setMinimumHeight(100)
                form_layout.addRow("段落内容:", self.text_input)
                
                # ID属性
                self.id_input = QLineEdit()
                self.id_input.setPlaceholderText("可选: 元素ID")
                form_layout.addRow("ID:", self.id_input)
                
                # 类属性
                self.class_input = QLineEdit()
                self.class_input.setPlaceholderText("可选: CSS类名")
                form_layout.addRow("CSS类:", self.class_input)
                
            elif self.element_type == "按钮":
                # 按钮文本
                self.text_input = QLineEdit()
                self.text_input.setPlaceholderText("按钮文本")
                form_layout.addRow("按钮文本:", self.text_input)
                
                # 按钮类型
                self.type_combo = QComboBox()
                self.type_combo.addItems(["按钮", "提交", "重置"])
                form_layout.addRow("按钮类型:", self.type_combo)
                
                # 按钮样式
                self.style_combo = QComboBox()
                self.style_combo.addItems(["默认", "主要", "次要", "成功", "警告", "危险", "链接"])
                form_layout.addRow("按钮样式:", self.style_combo)
                
                # ID属性
                self.id_input = QLineEdit()
                self.id_input.setPlaceholderText("可选: 元素ID")
                form_layout.addRow("ID:", self.id_input)
                
                # 类属性
                self.class_input = QLineEdit()
                self.class_input.setPlaceholderText("可选: CSS类名")
                form_layout.addRow("CSS类:", self.class_input)
                
            elif self.element_type == "图片":
                # 图片URL
                self.src_input = QLineEdit()
                self.src_input.setPlaceholderText("图片地址")
                form_layout.addRow("图片URL:", self.src_input)
                
                # 替代文本
                self.alt_input = QLineEdit()
                self.alt_input.setPlaceholderText("图片描述")
                form_layout.addRow("替代文本:", self.alt_input)
                
                # 宽度
                self.width_input = QLineEdit()
                self.width_input.setPlaceholderText("宽度 (像素)")
                form_layout.addRow("宽度:", self.width_input)
                
                # 高度
                self.height_input = QLineEdit()
                self.height_input.setPlaceholderText("高度 (像素)")
                form_layout.addRow("高度:", self.height_input)
                
                # ID属性
                self.id_input = QLineEdit()
                self.id_input.setPlaceholderText("可选: 元素ID")
                form_layout.addRow("ID:", self.id_input)
                
                # 类属性
                self.class_input = QLineEdit()
                self.class_input.setPlaceholderText("可选: CSS类名")
                form_layout.addRow("CSS类:", self.class_input)
                
            elif self.element_type == "链接":
                # 链接文本
                self.text_input = QLineEdit()
                self.text_input.setPlaceholderText("链接文本")
                form_layout.addRow("链接文本:", self.text_input)
                
                # 链接URL
                self.href_input = QLineEdit()
                self.href_input.setPlaceholderText("链接地址")
                form_layout.addRow("链接URL:", self.href_input)
                
                # 打开方式
                self.target_combo = QComboBox()
                self.target_combo.addItems(["当前窗口", "新窗口"])
                form_layout.addRow("打开方式:", self.target_combo)
                
                # ID属性
                self.id_input = QLineEdit()
                self.id_input.setPlaceholderText("可选: 元素ID")
                form_layout.addRow("ID:", self.id_input)
                
                # 类属性
                self.class_input = QLineEdit()
                self.class_input.setPlaceholderText("可选: CSS类名")
                form_layout.addRow("CSS类:", self.class_input)
                
            elif self.element_type == "容器":
                # 容器ID
                self.id_input = QLineEdit()
                self.id_input.setPlaceholderText("容器ID")
                form_layout.addRow("ID:", self.id_input)
                
                # 容器类名
                self.class_input = QLineEdit()
                self.class_input.setPlaceholderText("CSS类名")
                form_layout.addRow("CSS类:", self.class_input)
                
                # 容器类型
                self.type_combo = QComboBox()
                self.type_combo.addItems(["div", "section", "article", "header", "footer", "nav", "aside"])
                form_layout.addRow("容器类型:", self.type_combo)
                
                # 内部HTML
                self.html_input = QTextEdit()
                self.html_input.setPlaceholderText("可选: 内部HTML内容")
                self.html_input.setMinimumHeight(100)
                form_layout.addRow("内部内容:", self.html_input)
                
            elif self.element_type == "列表":
                # 列表类型
                self.type_combo = QComboBox()
                self.type_combo.addItems(["无序列表 (ul)", "有序列表 (ol)"])
                form_layout.addRow("列表类型:", self.type_combo)
                
                # 列表项
                self.items_group = QGroupBox("列表项")
                items_layout = QVBoxLayout(self.items_group)
                
                self.items_scroll = QScrollArea()
                self.items_scroll.setWidgetResizable(True)
                
                self.items_container = QWidget()
                self.items_container_layout = QVBoxLayout(self.items_container)
                
                # 添加几个默认列表项
                for i in range(3):
                    item_input = QLineEdit()
                    item_input.setPlaceholderText(f"列表项 {i+1}")
                    self.items_container_layout.addWidget(item_input)
                
                self.items_container_layout.addStretch()
                self.items_scroll.setWidget(self.items_container)
                self.items_scroll.setMinimumHeight(150)
                
                items_layout.addWidget(self.items_scroll)
                
                # 添加/删除按钮
                buttons_layout = QHBoxLayout()
                add_btn = QPushButton("添加项目")
                add_btn.clicked.connect(self.add_list_item)
                remove_btn = QPushButton("删除项目")
                remove_btn.clicked.connect(self.remove_list_item)
                buttons_layout.addWidget(add_btn)
                buttons_layout.addWidget(remove_btn)
                items_layout.addLayout(buttons_layout)
                
                form_layout.addRow(self.items_group)
                
                # ID属性
                self.id_input = QLineEdit()
                self.id_input.setPlaceholderText("可选: 元素ID")
                form_layout.addRow("ID:", self.id_input)
                
                # 类属性
                self.class_input = QLineEdit()
                self.class_input.setPlaceholderText("可选: CSS类名")
                form_layout.addRow("CSS类:", self.class_input)
            
            layout.addLayout(form_layout)
            
            # 底部按钮
            buttons_layout = QHBoxLayout()
            buttons_layout.addStretch()
            
            cancel_btn = QPushButton("取消")
            cancel_btn.clicked.connect(self.reject)
            
            ok_btn = QPushButton("确定")
            ok_btn.clicked.connect(self.accept)
            
            buttons_layout.addWidget(cancel_btn)
            buttons_layout.addWidget(ok_btn)
            
            layout.addLayout(buttons_layout)
        
        def add_list_item(self):
            # 添加新的列表项输入框
            item_input = QLineEdit()
            count = self.items_container_layout.count()
            item_input.setPlaceholderText(f"列表项 {count}")
            # 在伸缩空间之前插入
            self.items_container_layout.insertWidget(self.items_container_layout.count() - 1, item_input)
        
        def remove_list_item(self):
            # 移除最后一个列表项
            if self.items_container_layout.count() > 1:  # 至少保留一个伸缩空间
                item = self.items_container_layout.itemAt(self.items_container_layout.count() - 2)
                if item and isinstance(item.widget(), QLineEdit):
                    self.items_container_layout.removeWidget(item.widget())
                    item.widget().deleteLater()
        
        def accept(self):
            # 生成HTML代码
            self.result = self.generate_html()
            super().accept()
        
        def generate_html(self):
            # 根据元素类型生成对应的HTML代码
            if self.element_type == "标题":
                level = self.level_combo.currentText().split()[0]  # 获取h1, h2等
                text = self.text_input.text() if hasattr(self, 'text_input') else ''
                id_attr = f' id="{self.id_input.text()}"' if hasattr(self, 'id_input') and self.id_input.text() else ''
                class_attr = f' class="{self.class_input.text()}"' if hasattr(self, 'class_input') and self.class_input.text() else ''
                return f'<{level}{id_attr}{class_attr}>{text}</{level}>'
                
            elif self.element_type == "段落":
                text = self.text_input.toPlainText() if hasattr(self, 'text_input') else ''
                id_attr = f' id="{self.id_input.text()}"' if hasattr(self, 'id_input') and self.id_input.text() else ''
                class_attr = f' class="{self.class_input.text()}"' if hasattr(self, 'class_input') and self.class_input.text() else ''
                return f'<p{id_attr}{class_attr}>{text}</p>'
                
            elif self.element_type == "按钮":
                text = self.text_input.text() if hasattr(self, 'text_input') else ''
                type_map = {"按钮": "button", "提交": "submit", "重置": "reset"}
                type_val = type_map.get(self.type_combo.currentText(), "button")
                id_attr = f' id="{self.id_input.text()}"' if hasattr(self, 'id_input') and self.id_input.text() else ''
                
                # 添加样式类
                button_style = self.style_combo.currentText().lower()
                class_attr = f' class="btn btn-{button_style}"' 
                if hasattr(self, 'class_input') and self.class_input.text():
                    class_attr = f' class="{self.class_input.text()} btn btn-{button_style}"'
                
                return f'<button{id_attr}{class_attr} type="{type_val}">{text}</button>'
                
            elif self.element_type == "图片":
                src = self.src_input.text() if hasattr(self, 'src_input') else ''
                alt = self.alt_input.text() if hasattr(self, 'alt_input') else ''
                width_attr = f' width="{self.width_input.text()}"' if hasattr(self, 'width_input') and self.width_input.text() else ''
                height_attr = f' height="{self.height_input.text()}"' if hasattr(self, 'height_input') and self.height_input.text() else ''
                id_attr = f' id="{self.id_input.text()}"' if hasattr(self, 'id_input') and self.id_input.text() else ''
                class_attr = f' class="{self.class_input.text()}"' if hasattr(self, 'class_input') and self.class_input.text() else ''
                return f'<img src="{src}" alt="{alt}"{width_attr}{height_attr}{id_attr}{class_attr}>'
                
            elif self.element_type == "链接":
                text = self.text_input.text() if hasattr(self, 'text_input') else ''
                href = self.href_input.text() if hasattr(self, 'href_input') else ''
                target = "_blank" if hasattr(self, 'target_combo') and self.target_combo.currentText() == "新窗口" else "_self"
                id_attr = f' id="{self.id_input.text()}"' if hasattr(self, 'id_input') and self.id_input.text() else ''
                class_attr = f' class="{self.class_input.text()}"' if hasattr(self, 'class_input') and self.class_input.text() else ''
                return f'<a href="{href}" target="{target}"{id_attr}{class_attr}>{text}</a>'
                
            elif self.element_type == "容器":
                container_type = self.type_combo.currentText() if hasattr(self, 'type_combo') else 'div'
                id_attr = f' id="{self.id_input.text()}"' if hasattr(self, 'id_input') and self.id_input.text() else ''
                class_attr = f' class="{self.class_input.text()}"' if hasattr(self, 'class_input') and self.class_input.text() else ''
                inner_html = self.html_input.toPlainText() if hasattr(self, 'html_input') and self.html_input.toPlainText() else ''
                return f'<{container_type}{id_attr}{class_attr}>{inner_html}</{container_type}>'
                
            elif self.element_type == "列表":
                list_type = "ul" if hasattr(self, 'type_combo') and self.type_combo.currentText() == "无序列表 (ul)" else "ol"
                id_attr = f' id="{self.id_input.text()}"' if hasattr(self, 'id_input') and self.id_input.text() else ''
                class_attr = f' class="{self.class_input.text()}"' if hasattr(self, 'class_input') and self.class_input.text() else ''
                
                # 生成列表项
                items_html = []
                for i in range(self.items_container_layout.count()):
                    item = self.items_container_layout.itemAt(i)
                    if item and isinstance(item.widget(), QLineEdit) and item.widget().text():
                        items_html.append(f"<li>{item.widget().text()}</li>")
                
                return f'<{list_type}{id_attr}{class_attr}>\n    ' + '\n    '.join(items_html) + f'\n</{list_type}>'
                
            return ''
    
    # CSS样式编辑器对话框
    class CSSStyleEditor(QDialog):
        def __init__(self, style_type, parent=None):
            super().__init__(parent)
            self.setWindowTitle(f'编辑{style_type}样式')
            self.resize(400, 300)
            self.style_type = style_type
            self.result = None
            self.setup_ui()
        
        def setup_ui(self):
            layout = QVBoxLayout(self)
            self.setStyleSheet("""
                QDialog { background-color: #f0f0f0; }
                QLabel { color: #333333; font-weight: bold; margin-top: 10px; }
                QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox { 
                    background-color: #ffffff; 
                    color: #333333; 
                    border: 1px solid #cccccc; 
                    border-radius: 4px; 
                    padding: 8px; 
                    margin-bottom: 10px; 
                }
                QPushButton { 
                    background-color: #4a90e2; 
                    color: #ffffff; 
                    border: none; 
                    border-radius: 4px; 
                    padding: 8px 16px; 
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #5b9cf2; }
            """)
            
            form_layout = QFormLayout()
            
            # 选择器输入
            self.selector_input = QLineEdit()
            self.selector_input.setPlaceholderText("CSS选择器 (例如: body, .container, #header)")
            form_layout.addRow("CSS选择器:", self.selector_input)
            
            # 根据样式类型设置不同的输入字段
            if self.style_type == "背景色":
                # 背景颜色选择器
                color_layout = QHBoxLayout()
                self.color_input = QLineEdit()
                self.color_input.setText("#ffffff")
                color_layout.addWidget(self.color_input)
                
                self.color_btn = QPushButton("选择颜色")
                self.color_btn.clicked.connect(self.select_color)
                color_layout.addWidget(self.color_btn)
                
                form_layout.addRow("背景颜色:", color_layout)
                
                # 透明度滑块
                self.opacity_slider = QSlider(Qt.Horizontal)
                self.opacity_slider.setMinimum(0)
                self.opacity_slider.setMaximum(100)
                self.opacity_slider.setValue(100)
                self.opacity_slider.setTickInterval(10)
                self.opacity_slider.setTickPosition(QSlider.TicksBelow)
                self.opacity_slider.valueChanged.connect(lambda: self.opacity_label.setText(f"透明度: {self.opacity_slider.value()}%"))
                
                self.opacity_label = QLabel("透明度: 100%")
                self.opacity_label.setStyleSheet(f"color: {Theme.TEXT.name()};")
                
                form_layout.addRow(self.opacity_label)
                form_layout.addRow(self.opacity_slider)
                
            elif self.style_type == "文字颜色":
                # 文字颜色选择器
                color_layout = QHBoxLayout()
                self.color_input = QLineEdit()
                self.color_input.setText("#000000")
                color_layout.addWidget(self.color_input)
                
                self.color_btn = QPushButton("选择颜色")
                self.color_btn.clicked.connect(self.select_color)
                color_layout.addWidget(self.color_btn)
                
                form_layout.addRow("文字颜色:", color_layout)
                
                # 字体选择器
                font_layout = QHBoxLayout()
                self.font_family = QComboBox()
                self.font_family.addItems(["Arial", "Helvetica", "Times New Roman", "Georgia", "Verdana", "Courier New", "SimSun", "Microsoft YaHei"])
                font_layout.addWidget(self.font_family)
                
                self.font_size = QSpinBox()
                self.font_size.setMinimum(8)
                self.font_size.setMaximum(72)
                self.font_size.setValue(16)
                font_layout.addWidget(self.font_size)
                font_layout.addWidget(QLabel("px"))
                
                form_layout.addRow("字体:", font_layout)
                
            elif self.style_type == "字体大小":
                # 字体大小输入
                size_layout = QHBoxLayout()
                self.font_size = QDoubleSpinBox()
                self.font_size.setMinimum(8)
                self.font_size.setMaximum(72)
                self.font_size.setValue(16)
                size_layout.addWidget(self.font_size)
                
                self.size_unit = QComboBox()
                self.size_unit.addItems(["px", "em", "rem", "%", "vh", "vw"])
                size_layout.addWidget(self.size_unit)
                
                form_layout.addRow("字体大小:", size_layout)
                
                # 字体样式
                self.font_style = QComboBox()
                self.font_style.addItems(["常规", "斜体", "粗体", "粗斜体"])
                form_layout.addRow("字体样式:", self.font_style)
                
            elif self.style_type == "添加边距":
                # 边距设置
                margin_layout = QGridLayout()
                
                # 上边距
                margin_layout.addWidget(QLabel("上边距:"), 0, 0)
                self.margin_top = QSpinBox()
                self.margin_top.setMinimum(0)
                self.margin_top.setMaximum(200)
                self.margin_top.setValue(0)
                margin_layout.addWidget(self.margin_top, 0, 1)
                margin_layout.addWidget(QLabel("px"), 0, 2)
                
                # 右边距
                margin_layout.addWidget(QLabel("右边距:"), 1, 0)
                self.margin_right = QSpinBox()
                self.margin_right.setMinimum(0)
                self.margin_right.setMaximum(200)
                self.margin_right.setValue(0)
                margin_layout.addWidget(self.margin_right, 1, 1)
                margin_layout.addWidget(QLabel("px"), 1, 2)
                
                # 下边距
                margin_layout.addWidget(QLabel("下边距:"), 2, 0)
                self.margin_bottom = QSpinBox()
                self.margin_bottom.setMinimum(0)
                self.margin_bottom.setMaximum(200)
                self.margin_bottom.setValue(0)
                margin_layout.addWidget(self.margin_bottom, 2, 1)
                margin_layout.addWidget(QLabel("px"), 2, 2)
                
                # 左边距
                margin_layout.addWidget(QLabel("左边距:"), 3, 0)
                self.margin_left = QSpinBox()
                self.margin_left.setMinimum(0)
                self.margin_left.setMaximum(200)
                self.margin_left.setValue(0)
                margin_layout.addWidget(self.margin_left, 3, 1)
                margin_layout.addWidget(QLabel("px"), 3, 2)
                
                # 统一设置
                self.uniform_checkbox = QCheckBox("所有边距相同")
                self.uniform_checkbox.stateChanged.connect(self.toggle_uniform_margin)
                margin_layout.addWidget(self.uniform_checkbox, 4, 0, 1, 3)
                
                form_layout.addRow(margin_layout)
                
            elif self.style_type == "添加阴影":
                # 阴影设置
                shadow_layout = QVBoxLayout()
                
                # 水平偏移
                h_layout = QHBoxLayout()
                h_layout.addWidget(QLabel("水平偏移:"))
                self.shadow_h = QSpinBox()
                self.shadow_h.setMinimum(-50)
                self.shadow_h.setMaximum(50)
                self.shadow_h.setValue(0)
                h_layout.addWidget(self.shadow_h)
                h_layout.addWidget(QLabel("px"))
                shadow_layout.addLayout(h_layout)
                
                # 垂直偏移
                v_layout = QHBoxLayout()
                v_layout.addWidget(QLabel("垂直偏移:"))
                self.shadow_v = QSpinBox()
                self.shadow_v.setMinimum(-50)
                self.shadow_v.setMaximum(50)
                self.shadow_v.setValue(4)
                v_layout.addWidget(self.shadow_v)
                v_layout.addWidget(QLabel("px"))
                shadow_layout.addLayout(v_layout)
                
                # 模糊半径
                blur_layout = QHBoxLayout()
                blur_layout.addWidget(QLabel("模糊半径:"))
                self.shadow_blur = QSpinBox()
                self.shadow_blur.setMinimum(0)
                self.shadow_blur.setMaximum(100)
                self.shadow_blur.setValue(8)
                blur_layout.addWidget(self.shadow_blur)
                blur_layout.addWidget(QLabel("px"))
                shadow_layout.addLayout(blur_layout)
                
                # 阴影颜色
                color_layout = QHBoxLayout()
                self.shadow_color = QLineEdit()
                self.shadow_color.setText("rgba(0,0,0,0.1)")
                color_layout.addWidget(self.shadow_color)
                
                self.color_btn = QPushButton("选择颜色")
                self.color_btn.clicked.connect(self.select_shadow_color)
                color_layout.addWidget(self.color_btn)
                shadow_layout.addLayout(color_layout)
                
                # 内阴影选项
                self.inset_checkbox = QCheckBox("内阴影")
                shadow_layout.addWidget(self.inset_checkbox)
                
                form_layout.addRow(shadow_layout)
                
            elif self.style_type == "设置圆角":
                # 圆角设置
                radius_layout = QGridLayout()
                
                # 所有角
                radius_layout.addWidget(QLabel("所有角:"), 0, 0)
                self.radius_all = QSpinBox()
                self.radius_all.setMinimum(0)
                self.radius_all.setMaximum(100)
                self.radius_all.setValue(4)
                radius_layout.addWidget(self.radius_all, 0, 1)
                radius_layout.addWidget(QLabel("px"), 0, 2)
                
                # 单独设置选项
                self.separate_checkbox = QCheckBox("单独设置每个角")
                self.separate_checkbox.stateChanged.connect(self.toggle_separate_radius)
                radius_layout.addWidget(self.separate_checkbox, 1, 0, 1, 3)
                
                # 单独角设置
                self.radius_top_left = QSpinBox()
                self.radius_top_left.setMinimum(0)
                self.radius_top_left.setMaximum(100)
                self.radius_top_left.setValue(4)
                radius_layout.addWidget(QLabel("左上角:"), 2, 0)
                radius_layout.addWidget(self.radius_top_left, 2, 1)
                radius_layout.addWidget(QLabel("px"), 2, 2)
                
                self.radius_top_right = QSpinBox()
                self.radius_top_right.setMinimum(0)
                self.radius_top_right.setMaximum(100)
                self.radius_top_right.setValue(4)
                radius_layout.addWidget(QLabel("右上角:"), 3, 0)
                radius_layout.addWidget(self.radius_top_right, 3, 1)
                radius_layout.addWidget(QLabel("px"), 3, 2)
                
                self.radius_bottom_left = QSpinBox()
                self.radius_bottom_left.setMinimum(0)
                self.radius_bottom_left.setMaximum(100)
                self.radius_bottom_left.setValue(4)
                radius_layout.addWidget(QLabel("左下角:"), 4, 0)
                radius_layout.addWidget(self.radius_bottom_left, 4, 1)
                radius_layout.addWidget(QLabel("px"), 4, 2)
                
                self.radius_bottom_right = QSpinBox()
                self.radius_bottom_right.setMinimum(0)
                self.radius_bottom_right.setMaximum(100)
                self.radius_bottom_right.setValue(4)
                radius_layout.addWidget(QLabel("右下角:"), 5, 0)
                radius_layout.addWidget(self.radius_bottom_right, 5, 1)
                radius_layout.addWidget(QLabel("px"), 5, 2)
                
                # 初始隐藏单独设置
                for i in range(2, 6):
                    for j in range(3):
                        radius_layout.itemAtPosition(i, j).widget().setVisible(False)
                
                form_layout.addRow(radius_layout)
            
            layout.addLayout(form_layout)
            
            # 底部按钮
            buttons_layout = QHBoxLayout()
            buttons_layout.addStretch()
            
            cancel_btn = QPushButton("取消")
            cancel_btn.clicked.connect(self.reject)
            
            ok_btn = QPushButton("确定")
            ok_btn.clicked.connect(self.accept)
            
            buttons_layout.addWidget(cancel_btn)
            buttons_layout.addWidget(ok_btn)
            
            layout.addLayout(buttons_layout)
        
        def select_color(self):
            # 打开颜色选择器
            color = QColorDialog.getColor(QColor(self.color_input.text()), self, "选择颜色")
            if color.isValid():
                self.color_input.setText(color.name())
        
        def select_shadow_color(self):
            # 打开颜色选择器
            color = QColorDialog.getColor(QColor(self.shadow_color.text()), self, "选择阴影颜色")
            if color.isValid():
                # 转换为rgba格式，保留透明度
                self.shadow_color.setText(f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()/255:.2f})")
        
        def toggle_uniform_margin(self):
            # 切换统一边距设置
            is_checked = self.uniform_checkbox.isChecked()
            widgets = [self.margin_right, self.margin_bottom, self.margin_left]
            labels = [QLabel("右边距:"), QLabel("下边距:"), QLabel("左边距:")]
            px_labels = [QLabel("px"), QLabel("px"), QLabel("px")]
            
            for w in widgets + labels + px_labels:
                w.setEnabled(not is_checked)
        
        def toggle_separate_radius(self):
            # 切换单独圆角设置
            is_checked = self.separate_checkbox.isChecked()
            for i in range(2, 6):
                for j in range(3):
                    radius_layout.itemAtPosition(i, j).widget().setVisible(is_checked)
        
        def accept(self):
            # 生成CSS代码
            self.result = self.generate_css()
            super().accept()
        
        def generate_css(self):
            # 获取选择器
            selector = self.selector_input.text() if hasattr(self, 'selector_input') and self.selector_input.text() else '*'
            
            # 根据样式类型生成对应的CSS代码
            if self.style_type == "背景色":
                color = self.color_input.text() if hasattr(self, 'color_input') else '#ffffff'
                opacity = self.opacity_slider.value() / 100 if hasattr(self, 'opacity_slider') else 1.0
                
                # 处理透明度
                if opacity < 1.0 and color.startswith('#'):
                    # 转换为rgba
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)
                    color = f"rgba({r}, {g}, {b}, {opacity:.2f})"
                
                return f"{selector} {{ background-color: {color}; }}"
                
            elif self.style_type == "文字颜色":
                color = self.color_input.text() if hasattr(self, 'color_input') else '#000000'
                font_family = self.font_family.currentText() if hasattr(self, 'font_family') else 'Arial'
                font_size = self.font_size.value() if hasattr(self, 'font_size') else 16
                
                return f"{selector} {{ color: {color}; font-family: '{font_family}', sans-serif; font-size: {font_size}px; }}"
                
            elif self.style_type == "字体大小":
                font_size = self.font_size.value() if hasattr(self, 'font_size') else 16
                unit = self.size_unit.currentText() if hasattr(self, 'size_unit') else 'px'
                
                # 字体样式映射
                style_map = {"常规": "normal", "斜体": "italic", "粗体": "bold", "粗斜体": "bold italic"}
                font_style = style_map.get(self.font_style.currentText(), "normal")
                
                return f"{selector} {{ font-size: {font_size}{unit}; font-style: {font_style}; }}"
                
            elif self.style_type == "添加边距":
                # 检查是否使用统一边距
                if hasattr(self, 'uniform_checkbox') and self.uniform_checkbox.isChecked():
                    margin = self.margin_top.value()
                    return f"{selector} {{ margin: {margin}px; }}"
                else:
                    top = self.margin_top.value() if hasattr(self, 'margin_top') else 0
                    right = self.margin_right.value() if hasattr(self, 'margin_right') else 0
                    bottom = self.margin_bottom.value() if hasattr(self, 'margin_bottom') else 0
                    left = self.margin_left.value() if hasattr(self, 'margin_left') else 0
                    return f"{selector} {{ margin: {top}px {right}px {bottom}px {left}px; }}"
                
            elif self.style_type == "添加阴影":
                h = self.shadow_h.value() if hasattr(self, 'shadow_h') else 0
                v = self.shadow_v.value() if hasattr(self, 'shadow_v') else 4
                blur = self.shadow_blur.value() if hasattr(self, 'shadow_blur') else 8
                color = self.shadow_color.text() if hasattr(self, 'shadow_color') else "rgba(0,0,0,0.1)"
                inset = " inset" if hasattr(self, 'inset_checkbox') and self.inset_checkbox.isChecked() else ""
                
                return f"{selector} {{ box-shadow: {h}px {v}px {blur}px {color}{inset}; }}"
                
            elif self.style_type == "设置圆角":
                # 检查是否使用单独圆角
                if hasattr(self, 'separate_checkbox') and self.separate_checkbox.isChecked():
                    tl = self.radius_top_left.value() if hasattr(self, 'radius_top_left') else 4
                    tr = self.radius_top_right.value() if hasattr(self, 'radius_top_right') else 4
                    br = self.radius_bottom_right.value() if hasattr(self, 'radius_bottom_right') else 4
                    bl = self.radius_bottom_left.value() if hasattr(self, 'radius_bottom_left') else 4
                    return f"{selector} {{ border-radius: {tl}px {tr}px {br}px {bl}px; }}"
                else:
                    radius = self.radius_all.value() if hasattr(self, 'radius_all') else 4
                    return f"{selector} {{ border-radius: {radius}px; }}"
                
            return ''
    
    # JavaScript交互编辑器对话框
    class JSInteractionEditor(QDialog):
        def __init__(self, interaction_type, parent=None):
            super().__init__(parent)
            self.setWindowTitle(f'编辑{interaction_type}交互')
            self.resize(500, 400)
            self.interaction_type = interaction_type
            self.result = None
            self.setup_ui()
        
        def setup_ui(self):
            layout = QVBoxLayout(self)
            self.setStyleSheet("""
                QDialog { background-color: #f0f0f0; }
                QLabel { color: #333333; font-weight: bold; margin-top: 10px; }
                QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox { 
                    background-color: #ffffff; 
                    color: #333333; 
                    border: 1px solid #cccccc; 
                    border-radius: 4px; 
                    padding: 8px; 
                    margin-bottom: 10px; 
                }
                QPushButton { 
                    background-color: #4a90e2; 
                    color: #ffffff; 
                    border: none; 
                    border-radius: 4px; 
                    padding: 8px 16px; 
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #5b9cf2; }
                QDialog {{ background-color: {Theme.BACKGROUND.name()}; }}
                QLabel {{ color: {Theme.TEXT.name()}; font-weight: bold; margin-top: 10px; }}
                QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{ 
                    background-color: {Theme.SURFACE_DARK.name()}; 
                    color: {Theme.TEXT.name()}; 
                    border: 1px solid {Theme.BORDER.name()}; 
                    border-radius: 4px; 
                    padding: 8px; 
                    margin-bottom: 10px; 
                }}
                QPushButton {{ 
                    background-color: {Theme.PRIMARY.name()}; 
                    color: {Theme.BACKGROUND.name()}; 
                    border: none; 
                    border-radius: 4px; 
                    padding: 8px 16px; 
                    font-weight: bold;
                }}
                QPushButton:hover {{ background-color: {Theme.SECONDARY.name()}; }}
            """)
            
            form_layout = QFormLayout()
            
            # 选择器输入
            self.selector_input = QLineEdit()
            self.selector_input.setPlaceholderText("元素选择器 (例如: #button, .class, document.getElementById('id'))")
            form_layout.addRow("元素选择器:", self.selector_input)
            
            # 根据交互类型设置不同的输入字段
            if self.interaction_type in ["点击事件", "鼠标悬停"]:
                # 事件处理代码
                form_layout.addRow("事件处理代码:")
                self.code_input = QTextEdit()
                self.code_input.setPlaceholderText("输入JavaScript代码...")
                self.code_input.setMinimumHeight(150)
                self.code_input.setLineWrapMode(QTextEdit.WidgetWidth)
                
                # 预设代码选项
                code_presets = QComboBox()
                code_presets.addItems([
                    "显示提示框", 
                    "隐藏元素", 
                    "显示元素", 
                    "改变元素内容", 
                    "添加CSS类", 
                    "移除CSS类", 
                    "切换CSS类", 
                    "改变背景颜色", 
                    "改变文字颜色", 
                    "改变元素大小"
                ])
                code_presets.currentTextChanged.connect(self.apply_code_preset)
                form_layout.addWidget(code_presets)
                form_layout.addRow(self.code_input)
                
            elif self.interaction_type == "显示提示":
                # 提示内容
                self.message_input = QLineEdit()
                self.message_input.setPlaceholderText("提示消息内容")
                form_layout.addRow("提示内容:", self.message_input)
                
                # 提示类型
                self.alert_type = QComboBox()
                self.alert_type.addItems(["普通提示 (alert)", "确认对话框 (confirm)", "输入对话框 (prompt)"])
                form_layout.addRow("提示类型:", self.alert_type)
                
            elif self.interaction_type == "改变内容":
                # 新内容
                self.content_input = QTextEdit()
                self.content_input.setPlaceholderText("新的内容")
                self.content_input.setMinimumHeight(100)
                form_layout.addRow("新内容:", self.content_input)
                
                # 内容类型
                self.content_type = QComboBox()
                self.content_type.addItems(["纯文本 (textContent)", "HTML内容 (innerHTML)", "值 (value)"])
                form_layout.addRow("内容类型:", self.content_type)
                
            elif self.interaction_type == "添加类":
                # 类名输入
                self.class_input = QLineEdit()
                self.class_input.setPlaceholderText("要添加的CSS类名")
                form_layout.addRow("CSS类名:", self.class_input)
                
            elif self.interaction_type in ["隐藏元素", "显示元素"]:
                # 显示/隐藏效果
                self.effect_type = QComboBox()
                if self.interaction_type == "隐藏元素":
                    self.effect_type.addItems(["立即隐藏 (display: none)", "淡出效果", "向上收起"])
                else:
                    self.effect_type.addItems(["立即显示", "淡入效果", "向下展开"])
                form_layout.addRow("效果类型:", self.effect_type)
                
                # 动画持续时间
                duration_layout = QHBoxLayout()
                self.duration_input = QDoubleSpinBox()
                self.duration_input.setMinimum(0.1)
                self.duration_input.setMaximum(5)
                self.duration_input.setSingleStep(0.1)
                self.duration_input.setValue(0.3)
                duration_layout.addWidget(self.duration_input)
                duration_layout.addWidget(QLabel("秒"))
                form_layout.addRow("动画持续时间:", duration_layout)
            
            layout.addLayout(form_layout)
            
            # 底部按钮
            buttons_layout = QHBoxLayout()
            buttons_layout.addStretch()
            
            cancel_btn = QPushButton("取消")
            cancel_btn.clicked.connect(self.reject)
            
            ok_btn = QPushButton("确定")
            ok_btn.clicked.connect(self.accept)
            
            buttons_layout.addWidget(cancel_btn)
            buttons_layout.addWidget(ok_btn)
            
            layout.addLayout(buttons_layout)
        
        def apply_code_preset(self, preset):
            # 根据预设填充代码
            if preset == "显示提示框":
                self.code_input.setPlainText("alert('Hello World!');")
            elif preset == "隐藏元素":
                self.code_input.setPlainText("this.style.display = 'none';")
            elif preset == "显示元素":
                self.code_input.setPlainText("this.style.display = 'block';")
            elif preset == "改变元素内容":
                self.code_input.setPlainText("this.textContent = '新内容';")
            elif preset == "添加CSS类":
                self.code_input.setPlainText("this.classList.add('active');")
            elif preset == "移除CSS类":
                self.code_input.setPlainText("this.classList.remove('active');")
            elif preset == "切换CSS类":
                self.code_input.setPlainText("this.classList.toggle('active');")
            elif preset == "改变背景颜色":
                self.code_input.setPlainText("this.style.backgroundColor = '#ff0000';")
            elif preset == "改变文字颜色":
                self.code_input.setPlainText("this.style.color = '#ffffff';")
            elif preset == "改变元素大小":
                self.code_input.setPlainText("this.style.width = '300px';")
        
        def accept(self):
            # 生成JavaScript代码
            self.result = self.generate_js()
            super().accept()
        
        def generate_js(self):
            # 获取选择器
            selector = self.selector_input.text() if hasattr(self, 'selector_input') else 'element'
            
            # 根据交互类型生成对应的JavaScript代码
            if self.interaction_type == "点击事件":
                code = self.code_input.toPlainText() if hasattr(self, 'code_input') else ''
                # 包装在事件监听器中
                return f"{selector}.addEventListener('click', function() {{{code}}});"
                
            elif self.interaction_type == "鼠标悬停":
                code = self.code_input.toPlainText() if hasattr(self, 'code_input') else ''
                # 包装在事件监听器中
                return f"{selector}.addEventListener('mouseover', function() {{{code}}});"
                
            elif self.interaction_type == "显示提示":
                message = self.message_input.text() if hasattr(self, 'message_input') else 'Hello World!'
                alert_type = self.alert_type.currentText()
                
                if "确认" in alert_type:
                    return f"if (confirm('{message}')) {{ /* 用户点击了确定按钮 */ }} else {{ /* 用户点击了取消按钮 */ }}"
                elif "输入" in alert_type:
                    return f"const userInput = prompt('{message}'); if (userInput !== null) {{ /* 使用用户输入的值 */ }}"
                else:
                    return f"alert('{message}');"
                
            elif self.interaction_type == "改变内容":
                content = self.content_input.toPlainText() if hasattr(self, 'content_input') else ''
                content_type = self.content_type.currentText()
                
                if "HTML" in content_type:
                    return f"{selector}.innerHTML = '{content}';"
                elif "值" in content_type:
                    return f"{selector}.value = '{content}';"
                else:  # 纯文本
                    return f"{selector}.textContent = '{content}';"
                
            elif self.interaction_type == "添加类":
                class_name = self.class_input.text() if hasattr(self, 'class_input') else 'active'
                return f"{selector}.classList.add('{class_name}');"
                
            elif self.interaction_type == "隐藏元素":
                effect = self.effect_type.currentText() if hasattr(self, 'effect_type') else ''
                duration = self.duration_input.value() if hasattr(self, 'duration_input') else 0.3
                
                if "淡出" in effect:
                    return f"{selector}.style.opacity = '0'; {selector}.style.transition = 'opacity {duration}s'; setTimeout(() => {{ {selector}.style.display = 'none'; }}, {duration*1000});"
                elif "收起" in effect:
                    return f"{selector}.style.maxHeight = '{selector}.scrollHeight + 'px'; {selector}.style.overflow = 'hidden'; {selector}.style.transition = 'max-height {duration}s'; {selector}.style.maxHeight = '0';"
                else:  # 立即隐藏
                    return f"{selector}.style.display = 'none';"
                
            elif self.interaction_type == "显示元素":
                effect = self.effect_type.currentText() if hasattr(self, 'effect_type') else ''
                duration = self.duration_input.value() if hasattr(self, 'duration_input') else 0.3
                
                if "淡入" in effect:
                    return f"{selector}.style.opacity = '0'; {selector}.style.display = 'block'; {selector}.style.transition = 'opacity {duration}s'; setTimeout(() => {{ {selector}.style.opacity = '1'; }}, 10);"
                elif "展开" in effect:
                    return f"{selector}.style.maxHeight = '0'; {selector}.style.overflow = 'hidden'; {selector}.style.transition = 'max-height {duration}s'; {selector}.style.display = 'block'; {selector}.style.maxHeight = '{selector}.scrollHeight + 'px';"
                else:  # 立即显示
                    return f"{selector}.style.display = 'block';"
                
            return ''
    
    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('积木式Web开发工具')
        self.setGeometry(100, 100, 1600, 900)
        
        # 设置全局样式
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ 
                background-color: {Theme.BACKGROUND.name()}; 
                color: {Theme.TEXT.name()}; 
            }}
            QPushButton {{ 
                background-color: {Theme.PRIMARY.name()}; 
                color: {Theme.BACKGROUND.name()}; 
                border: none; 
                padding: 8px 16px; 
                border-radius: 4px; 
                font-weight: bold;
            }}
            QPushButton:hover {{ 
                background-color: {Theme.SECONDARY.name()}; 
            }}
            QTabWidget::pane {{ 
                border: 1px solid {Theme.SURFACE.name()}; 
                background-color: {Theme.BACKGROUND.name()}; 
            }}
            QTabBar::tab {{ 
                background-color: {Theme.SURFACE.name()}; 
                color: {Theme.TEXT.name()}; 
                padding: 10px 20px; 
                border-top-left-radius: 5px; 
                border-top-right-radius: 5px;
            }}
            QTabBar::tab:selected {{ 
                background-color: {Theme.BACKGROUND.name()}; 
                color: {Theme.PRIMARY.name()}; 
                font-weight: bold;
            }}
        """)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 创建顶部工具栏
        self.create_toolbar()
        
        # 创建主要区域的分割器
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 创建左侧区域（组件面板和编辑区）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 可视化编程标签
        visual_tab = QWidget()
        visual_layout = QVBoxLayout(visual_tab)
        
        # 顶部面板分割器
        top_splitter = QSplitter(Qt.Vertical)
        
        # 创建组件面板
        self.create_block_palette(top_splitter)
        
        # 创建积木编辑区
        self.block_editor = BlockEditor(self)
        top_splitter.addWidget(self.block_editor)
        top_splitter.setSizes([300, 400])
        
        visual_layout.addWidget(top_splitter)
        
        # 代码编辑标签
        code_tab = QWidget()
        code_layout = QVBoxLayout(code_tab)
        
        # 创建代码编辑标签页
        code_editor_tab = QTabWidget()
        
        self.html_editor = CodeEditor()
        self.css_editor = CodeEditor()
        self.js_editor = CodeEditor()
        
        # 设置默认内容
        self.html_editor.setPlainText('<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>我的积木式网页</title>\n    <style>\n        /* CSS样式将自动生成 */\n    </style>\n</head>\n<body>\n    <!-- HTML内容将自动生成 -->\n    <script>\n        // JavaScript代码将自动生成\n    </script>\n</body>\n</html>')
        
        self.css_editor.setPlainText('body {\n    font-family: Arial, sans-serif;\n    line-height: 1.6;\n    margin: 0;\n    padding: 20px;\n    background-color: #f0f0f0;\n}\n\n.container {\n    max-width: 1200px;\n    margin: 0 auto;\n    background-color: white;\n    padding: 20px;\n    border-radius: 8px;\n    box-shadow: 0 2px 10px rgba(0,0,0,0.1);\n}')
        
        self.js_editor.setPlainText('// 等待页面加载完成\ndocument.addEventListener("DOMContentLoaded", function() {\n    console.log("页面已加载完成");\n    // JavaScript代码将在这里生成\n});')
        
        code_editor_tab.addTab(self.html_editor, 'HTML')
        code_editor_tab.addTab(self.css_editor, 'CSS')
        code_editor_tab.addTab(self.js_editor, 'JS')
        
        code_layout.addWidget(code_editor_tab)
        
        # 添加标签页到主标签页
        tab_widget.addTab(visual_tab, '可视化编程')
        tab_widget.addTab(code_tab, '代码编辑')
        
        left_layout.addWidget(tab_widget)
        
        # 创建右侧预览区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 预览工具栏
        preview_toolbar = QWidget()
        preview_toolbar_layout = QHBoxLayout(preview_toolbar)
        
        refresh_btn = QPushButton('刷新预览')
        refresh_btn.clicked.connect(self.update_preview)
        
        preview_label = QLabel('预览窗口')
        preview_label.setStyleSheet(f"color: {Theme.PRIMARY.name()}; font-weight: bold;")
        
        preview_toolbar_layout.addWidget(preview_label)
        preview_toolbar_layout.addStretch()
        preview_toolbar_layout.addWidget(refresh_btn)
        
        # 预览窗口
        self.preview_widget = QWebEngineView()
        
        right_layout.addWidget(preview_toolbar)
        right_layout.addWidget(self.preview_widget)
        
        # 将左侧和右侧添加到主分割器
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([800, 800])
        
        # 添加到主布局
        main_layout.addWidget(main_splitter)
        
        # 创建底部状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.setStyleSheet(f"background-color: {Theme.SURFACE.name()}; color: {Theme.TEXT.name()};")
        self.statusBar.showMessage('就绪 - 开始拖拽积木来创建你的网页吧！')
        
        # 连接信号
        self.html_editor.textChanged.connect(self.update_preview)
        self.css_editor.textChanged.connect(self.update_preview)
        self.js_editor.textChanged.connect(self.update_preview)
        
        # 初始更新预览
        self.update_preview()
    
    def create_toolbar(self):
        # 创建工具栏
        toolbar = QToolBar("主工具栏")
        # 设置工具栏和按钮的样式
        toolbar.setStyleSheet(f"QToolBar {{ background-color: {Theme.SURFACE.name()}; padding: 5px; spacing: 5px; }}")
        toolbar.setStyleSheet(toolbar.styleSheet() + f" QToolBar::item {{ background-color: {Theme.PRIMARY.name()}; color: {Theme.BACKGROUND.name()}; border-radius: 4px; padding: 2px; }}")
        toolbar.setStyleSheet(toolbar.styleSheet() + f" QToolBar::item:selected, QToolBar::item:pressed {{ background-color: {Theme.SECONDARY.name()}; }}")
        toolbar.setStyleSheet(toolbar.styleSheet() + f" QToolButton {{ color: {Theme.BACKGROUND.name()}; font-weight: bold; padding: 6px 14px; border-radius: 4px; }}")
        self.addToolBar(toolbar)
        
        # 创建新文件按钮
        new_action = QAction("新建项目", self)
        new_action.setToolTip("创建一个新的Web项目")
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        # 创建打开文件按钮
        open_action = QAction("打开项目", self)
        open_action.setToolTip("打开一个已有的HTML文件")
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        # 创建保存文件按钮
        save_action = QAction("保存项目", self)
        save_action.setToolTip("保存当前项目")
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        # 添加分隔符
        toolbar.addSeparator()
        
        # 创建运行预览按钮
        run_action = QAction("运行预览", self)
        run_action.setToolTip("更新预览窗口")
        run_action.triggered.connect(self.update_preview)
        toolbar.addAction(run_action)
    
    def create_block_palette(self, parent_widget):
        # 创建组件面板的标签页
        palette_tabs = QTabWidget()
        # 优化标签页样式
        palette_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #444; border-radius: 4px; background-color: #2d2d2d; }
            QTabBar::tab { background-color: #3d3d3d; color: #ffffff; padding: 8px 16px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background-color: #2d2d2d; color: #4a9eff; border-bottom: 2px solid #4a9eff; }
            QTabBar::tab:hover { background-color: #4a4a4a; }
        """)
        
        # HTML元素标签页
        html_palette = BlockPalette()
        html_elements = [
            ("添加标题", "motion", "<h1>标题文本</h1>", Theme.BLOCK_ANIMATION, "html_h1", {"text": "标题文本", "level": "1", "color": "#000000"}),
            ("添加段落", "motion", "<p>这是一个段落</p>", Theme.BLOCK_ANIMATION, "html_p", {"text": "这是一个段落", "color": "#000000", "align": "left"}),
            ("添加按钮", "motion", "<button>点击我</button>", Theme.BLOCK_ANIMATION, "html_button", {"text": "点击我", "color": "#ffffff", "bgcolor": "#007bff", "size": "medium"}),
            ("添加图片", "motion", "<img src='https://example.com/image.jpg' alt='图片'>", Theme.BLOCK_ANIMATION, "html_img", {"src": "https://example.com/image.jpg", "alt": "图片描述", "width": "300", "height": ""}),
            ("添加链接", "motion", "<a href='https://example.com'>链接文本</a>", Theme.BLOCK_ANIMATION, "html_a", {"href": "https://example.com", "text": "访问网站", "target": "_blank"}),
            ("添加容器", "motion", "<div class='container'></div>", Theme.BLOCK_ANIMATION, "html_div", {"class": "container", "bgcolor": "#f8f9fa", "padding": "20px"}),
            ("添加列表", "motion", "<ul><li>项目1</li><li>项目2</li></ul>", Theme.BLOCK_ANIMATION, "html_ul", {"items": ["项目1", "项目2"], "type": "ul"}),
        ]
        
        for name, block_type, code, color, elem_type, params in html_elements:
            item = BlockItem(name, block_type, code, color, element_type=elem_type, params=params)
            html_palette.addItem(item)
        
        # CSS样式标签页
        css_palette = BlockPalette()
        css_styles = [
            ("设置背景色", "looks", "body { background-color: #ffffff; }", Theme.BLOCK_LAYOUT, "css_bgcolor", {"selector": "body", "color": "#ffffff"}),
            ("设置文字颜色", "looks", "body { color: #000000; }", Theme.BLOCK_LAYOUT, "css_textcolor", {"selector": "body", "color": "#000000"}),
            ("设置字体大小", "looks", "body { font-size: 16px; }", Theme.BLOCK_LAYOUT, "css_fontsize", {"selector": "body", "size": "16"}),
            ("添加边距", "looks", "* { margin: 10px; }", Theme.BLOCK_LAYOUT, "css_margin", {"selector": "*", "top": "10", "right": "10", "bottom": "10", "left": "10"}),
            ("添加阴影", "looks", ".container { box-shadow: 0 4px 8px rgba(0,0,0,0.1); }", Theme.BLOCK_LAYOUT, "css_shadow", {"selector": ".container", "horizontal": "0", "vertical": "4", "blur": "8", "color": "rgba(0,0,0,0.1)"}),
            ("设置圆角", "looks", ".container { border-radius: 8px; }", Theme.BLOCK_LAYOUT, "css_borderradius", {"selector": ".container", "radius": "8"}),
        ]
        
        for name, block_type, code, color, elem_type, params in css_styles:
            item = BlockItem(name, block_type, code, color, element_type=elem_type, params=params)
            css_palette.addItem(item)
        
        # JavaScript交互标签页
        js_palette = BlockPalette()
        js_scripts = [
            ("点击事件", "events", "document.querySelector('button').addEventListener('click', function() { alert('点击了按钮!'); });", Theme.BLOCK_EVENT, "js_click", {"selector": "button", "action": "alert('点击了按钮!')"}),
            ("鼠标悬停", "events", "document.querySelector('.hoverable').addEventListener('mouseover', function() { this.style.backgroundColor = '#f0f0f0'; });", Theme.BLOCK_EVENT, "js_mouseover", {"selector": ".hoverable", "action": "this.style.backgroundColor = '#f0f0f0'"}),
            ("显示提示", "events", "alert('提示信息');", Theme.BLOCK_EVENT, "js_alert", {"message": "提示信息"}),
            ("改变内容", "control", "document.querySelector('#target').textContent = '新内容';", Theme.BLOCK_JS, "js_textcontent", {"selector": "#target", "text": "新内容"}),
            ("添加类", "control", "document.querySelector('.element').classList.add('active');", Theme.BLOCK_JS, "js_addclass", {"selector": ".element", "class": "active"}),
            ("隐藏元素", "control", "document.querySelector('.hidden').style.display = 'none';", Theme.BLOCK_JS, "js_hide", {"selector": ".hidden"}),
            ("显示元素", "control", "document.querySelector('.visible').style.display = 'block';", Theme.BLOCK_JS, "js_show", {"selector": ".visible", "display": "block"}),
        ]
        
        for name, block_type, code, color, elem_type, params in js_scripts:
            item = BlockItem(name, block_type, code, color, element_type=elem_type, params=params)
            js_palette.addItem(item)
        
        # 添加标签页
        palette_tabs.addTab(html_palette, "HTML元素")
        palette_tabs.addTab(css_palette, "样式")
        palette_tabs.addTab(js_palette, "交互")
        
        # 添加到父部件
        parent_widget.addWidget(palette_tabs)
    
    def update_code_from_blocks(self):
        # 从积木编辑区生成代码
        html_code = []
        css_code = []
        js_code = []
        
        for i in range(self.block_editor.count()):
            item = self.block_editor.item(i)
            code = item.code_template
            
            # 根据积木类型分类代码
            if code.strip().startswith('<'):
                html_code.append(code)
            elif '{' in code and '}' in code:
                css_code.append(code)
            else:
                js_code.append(code)
        
        # 更新编辑器内容
        self.update_merged_code(html_code, css_code, js_code)
        self.statusBar.showMessage('已从积木更新代码')
    
    def update_merged_code(self, html_parts, css_parts, js_parts):
        # 获取当前HTML内容
        html = self.html_editor.toPlainText()
        
        # 合并HTML部分
        if html_parts:
            body_start = html.find('<body>')
            body_end = html.find('</body>')
            if body_start != -1 and body_end != -1:
                # 保留原有的body内容，添加新内容
                body_content = '\n    ' + '\n    '.join(html_parts) + '\n'
                new_html = html[:body_start + 6] + body_content + html[body_end:]
                self.html_editor.setPlainText(new_html)
        
        # 合并CSS部分
        if css_parts:
            css = self.css_editor.toPlainText()
            # 添加新的CSS规则
            for css_part in css_parts:
                if css_part not in css:
                    css += '\n\n' + css_part
            self.css_editor.setPlainText(css)
        
        # 合并JS部分
        if js_parts:
            js = self.js_editor.toPlainText()
            dom_content = "document.addEventListener(\"DOMContentLoaded\", function() {"
            # 查找DOMContentLoaded事件处理函数
            if dom_content in js:
                # 在DOMContentLoaded函数内添加代码
                start = js.find(dom_content) + len(dom_content)
                end = js.rfind("});")
                if start != -1 and end != -1:
                    new_js_code = '\n    ' + '\n    '.join(js_parts) + '\n'
                    new_js = js[:start] + new_js_code + js[end:]
                    self.js_editor.setPlainText(new_js)
        
        # 更新预览
        self.update_preview()
    
    def update_preview(self):
        # 更新预览窗口
        html = self.html_editor.toPlainText()
        css = self.css_editor.toPlainText()
        js = self.js_editor.toPlainText()
        
        # 合并HTML、CSS和JS
        if '<style>' in html and '</style>' in html:
            start = html.find('<style>')
            end = html.find('</style>')
            html = html[:start + 7] + '\n' + css + '\n' + html[end:]
        else:
            if '<head>' in html:
                html = html.replace('<head>', f'<head>\n    <style>\n{css}\n    </style>')
            else:
                html = '<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="UTF-8">\n    <style>\n' + css + '\n    </style>\n</head>\n<body>\n' + \
                       html[html.find('<body>') + 6:html.rfind('</body>')] + '\n</body>\n</html>'
        
        if '<script>' in html and '</script>' in html:
            start = html.rfind('<script>')
            end = html.rfind('</script>')
            if start != -1 and end != -1:
                html = html[:start + 8] + '\n' + js + '\n' + html[end:]
        else:
            if '</body>' in html:
                html = html.replace('</body>', f'    <script>\n{js}\n    </script>\n</body>')
        
        # 设置预览内容
        self.preview_widget.setHtml(html)
        self.statusBar.showMessage('预览已更新')
    
    def new_file(self):
        # 新建文件
        reply = QMessageBox.question(self, '确认', '是否要创建新文件？当前未保存的内容将会丢失。',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.html_editor.clear()
            self.css_editor.clear()
            self.js_editor.clear()
            self.block_editor.clear()
            self.file_path = None
            self.setWindowTitle('积木式Web开发工具')
            self.statusBar.showMessage('已创建新文件')
            # 重置默认内容
            self.html_editor.setPlainText('<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>我的积木式网页</title>\n    <style>\n        /* CSS样式将自动生成 */\n    </style>\n</head>\n<body>\n    <!-- HTML内容将自动生成 -->\n    <script>\n        // JavaScript代码将自动生成\n    </script>\n</body>\n</html>')
    
    def open_file(self):
        # 打开文件
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "打开HTML文件", "", 
                                                  "HTML Files (*.html);;All Files (*)", options=options)
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    
                # 提取HTML内容
                self.html_editor.setPlainText(html_content)
                
                # 提取CSS内容
                css_start = html_content.find('<style>')
                css_end = html_content.find('</style>')
                if css_start != -1 and css_end != -1:
                    css_content = html_content[css_start + 7:css_end].strip()
                    self.css_editor.setPlainText(css_content)
                
                # 提取JavaScript内容
                js_start = html_content.find('<script>')
                js_end = html_content.find('</script>')
                if js_start != -1 and js_end != -1:
                    js_content = html_content[js_start + 8:js_end].strip()
                    self.js_editor.setPlainText(js_content)
                
                # 清空积木编辑器
                self.block_editor.clear()
                
                self.file_path = file_path
                self.setWindowTitle(f'积木式Web开发工具 - {os.path.basename(file_path)}')
                self.statusBar.showMessage(f'已打开文件: {os.path.basename(file_path)}')
                self.update_preview()
            except Exception as e:
                QMessageBox.critical(self, '错误', f'无法打开文件: {str(e)}')
    
    def save_file(self):
        # 保存文件
        if not self.file_path:
            self.save_file_as()
        else:
            self._save_current_file(self.file_path)
    
    def save_file_as(self):
        # 另存为文件
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "保存HTML文件", "",
                                                  "HTML Files (*.html);;All Files (*)", options=options)
        
        if file_path:
            self._save_current_file(file_path)
    
    def _save_current_file(self, file_path):
        try:
            html = self.html_editor.toPlainText()
            css = self.css_editor.toPlainText()
            js = self.js_editor.toPlainText()
            
            # 合并HTML、CSS和JS内容
            if '<style>' in html and '</style>' in html:
                start = html.find('<style>')
                end = html.find('</style>')
                html = html[:start + 7] + '\n' + css + '\n' + html[end:]
            else:
                if '<head>' in html:
                    html = html.replace('<head>', f'<head>\n    <style>\n{css}\n    </style>')
                else:
                    html = '<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="UTF-8">\n    <style>\n' + css + '\n    </style>\n</head>\n<body>\n' + \
                           html[html.find('<body>') + 6:html.rfind('</body>')] + '\n</body>\n</html>'
            
            if '<script>' in html and '</script>' in html:
                start = html.find('<script>')
                end = html.find('</script>')
                if start != -1 and end != -1:
                    html = html[:start + 8] + '\n' + js + '\n' + html[end:]
            else:
                if '</body>' in html:
                    html = html.replace('</body>', f'    <script>\n{js}\n    </script>\n</body>')
                else:
                    if '</html>' in html:
                        html = html.replace('</html>', '</body>\n    <script>\n' + js + '\n    </script>\n</html>')
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            self.file_path = file_path
            self.setWindowTitle(f'积木式Web开发工具 - {os.path.basename(file_path)}')
            self.statusBar.showMessage(f'已保存文件: {os.path.basename(file_path)}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法保存文件: {str(e)}')

if __name__ == '__main__':
    # 确保应用程序可以正常运行
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 使用Fusion样式以获得更好的跨平台一致性
    editor = ScratchWebEditor()
    editor.show()
    sys.exit(app.exec_())