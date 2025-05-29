import os
import json
import logging
import threading
from queue import Queue
from tkinter import Tk, Canvas, Frame, Scrollbar
from PIL import Image, ImageTk  # 使用 PIL 来处理图片

from sync.config_store import get_config, set_config

# 配置日志格式
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(threadName)s] %(levelname)s in %(module)s.%(funcName)s: %(message)s',
)


# 新增 Graph 类
class Graph(Canvas):
    '''Graphic elements are composed of line(segment), rectangle, ellipse, and arc.
    '''

    def __init__(self, master=None, cnf={}, **kw):
        '''The base class of all graphics frames.

        :param master: a widget of tkinter or tkinter.ttk.
        '''
        super().__init__(master, cnf, **kw)
        self.rectangle_selector = []
        self.tag_bind('current', "<ButtonPress-1>", self.scroll_start)
        self.tag_bind('current', "<B1-Motion>", self.scroll_move)

    def scroll_start(self, event):
        self.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.scan_dragto(event.x, event.y, gain=1)

    def create_mask(self, size, alpha, fill):
        """Create properly transparent overlay mask"""
        fill = (*self.master.winfo_rgb(fill), alpha)
        image = Image.new('RGBA', size, fill)
        return image

    def draw_rectangle(self, x1, y1, x2, y2, **kwargs):
        """Draw rectangle with proper overlay tracking"""
        if 'alpha' in kwargs:
            # Create transparent overlay
            overlay_id = self.create_rectangle(
                x1, y1, x2, y2,
                fill=kwargs.get('fill', 'black'),
                stipple='gray50',  # Makes it semi-transparent
                tags=('overlay', f'overlay_{x1}_{y1}')  # Unique tag for each overlay
            )
            return overlay_id
        return super().create_rectangle(x1, y1, x2, y2, **kwargs)

    def draw_rectangle_overlay(self, x1, y1, x2, y2, **kwargs):
        """Draw semi-transparent rectangle using PIL image overlay"""
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill', 'black')

            # Convert color name to RGB tuple and add alpha
            rgb = self.winfo_rgb(fill)
            rgba = (rgb[0] >> 8, rgb[1] >> 8, rgb[2] >> 8, alpha)  # Convert from 16-bit to 8-bit per channel

            width = x2 - x1
            height = y2 - y1

            # Create transparent overlay image
            overlay = Image.new('RGBA', (width, height), rgba)
            photo = ImageTk.PhotoImage(overlay)

            # Save reference to prevent garbage collection
            if not hasattr(self, 'overlay_images'):
                self.overlay_images = []
            self.overlay_images.append(photo)

            # 提取并处理 tags 参数
            tags = tuple(list(kwargs.get('tags', ())) + [f'overlay_{x1}_{y1}'])

            # Draw the image on canvas
            overlay_id = self.create_image(
                x1, y1,
                image=photo,
                anchor='nw',
                tags=tags # Unique tag for each overlay
            )
            # Optionally draw base rectangle border
            if kwargs.get('outline', True):
                super().create_rectangle(x1, y1, x2, y2, **kwargs)

            return overlay_id

    def delete_overlay(self, overlay):
        """
        删除指定 tag 的 overlay 图像
        :param tag: 要删除的 tag
        """
        self.overlay_images = []
        self.delete(overlay)

    def get_item_by_index(self, index):
        """
        根据索引获取对应的 Canvas 对象
        :param index: 图片索引
        :return: 对应的 Canvas 对象
        """
        return self.find_withtag(f"overlay_{index}")

    def get_object_bbox(self, obj_id):
        """
        获取指定对象的边界框坐标 (x1, y1, x2, y2)
        :param obj_id: 对象的 ID 或标签
        :return: 边界框坐标 (x1, y1, x2, y2)
        """
        return self.bbox(obj_id)


class ImageLoader:
    """Background image loader with caching"""

    def __init__(self, max_workers=4):
        self.queue = Queue()
        self.cache = {}
        self.lock = threading.Lock()
        self.loaded_flags = {}

        for _ in range(max_workers):
            threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        while True:
            task = self.queue.get()
            self._load_image(*task)
            self.queue.task_done()

    def _load_image(self, path, index, callback):
        try:
            img = Image.open(path)
            img = img.resize((100, 100))
            photo = ImageTk.PhotoImage(img)
            with self.lock:
                self.cache[index] = photo
                self.loaded_flags[index] = True
            callback(index, photo)
        except Exception as e:
            logging.error(f"Error loading {path}: {e}", exc_info=True)

    def get_or_queue(self, path, index, callback):
        with self.lock:
            if index in self.cache:
                return self.cache[index]
            self.queue.put((path, index, callback))
        return None

# 新增方法：窗口居中逻辑
def center_window(root, width_ratio=0.618, height_ratio=0.618):
    """
    将窗口居中到屏幕的黄金分割点，并调整窗口大小。
    :param root: Tkinter 主窗口
    :param width_ratio: 宽度比例（默认为黄金分割比例 0.618）
    :param height_ratio: 高度比例（默认为黄金分割比例 0.618）
    """
    # 获取屏幕宽度和高度
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 计算窗口宽度和高度
    window_width = int(screen_width * width_ratio)
    window_height = int(screen_height * height_ratio)

    # 计算窗口左上角的坐标
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    # 设置窗口大小和位置
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")


def update_config_includes(file_name, action):
    """
    更新配置文件中的 includes 列表。
    :param file_name: 文件名
    :param action: 'add' 或 'remove'
    """
    config = get_config("include_dirs", "[]")  # 从数据库中获取 includes 列表
    includes = json.loads(config)  # 将 JSON 字符串转换为 Python 列表

    key = file_name[:-4]
    if action == 'add' and key not in includes:
        includes.append(key)
    elif action == 'remove' and key in includes:
        includes.remove(key)

    set_config("include_dirs", json.dumps(includes))  # 将更新后的列表保存回数据库


def find_avatar_files(base_wechat_dir):
    """递归查找 Avatar 子文件夹中的 jpg 文件"""
    avatar_files = []
    for root, dirs, files in os.walk(base_wechat_dir):
        if "Avatar" in dirs:
            avatar_dir = os.path.join(root, "Avatar")
            for file in os.listdir(avatar_dir):
                if file.endswith(".jpg"):
                    avatar_files.append(os.path.join(avatar_dir, file))
    return avatar_files


def get_includes():
    """从数据库中获取 includes 列表，并缓存结果"""
    if not hasattr(get_includes, 'cached_includes'):
        get_includes.cached_includes = json.loads(get_config("include_dirs", "[]"))
    return get_includes.cached_includes


class ConfigParams:
    """配置值对象，管理网格参数、窗口位置参数和滚动管理参数"""
    def __init__(self):
        self.rows_per_column = 10  # 每列的行数
        self.columns = 10  # 列数
        self.padding_x = 5  # x 轴间距
        self.padding_y = 2  # y 轴间距
        self.width_ratio = 0.618  # 窗口宽度比例
        self.height_ratio = 0.618  # 窗口高度比例


def toggle_selection(canvas, index, file_name, action):
    """
    抽象的选中/反选逻辑
    :param canvas: 当前操作的画布对象
    :param index: 图片索引
    :param file_name: 文件名
    :param action: 'add' 或 'remove'
    """
    overlay_tag = f"overlay_{index}"
    overlays = canvas.find_withtag(overlay_tag)

    if overlays and action == 'remove':
        # 反选：移除蒙层并从 includes 移除文件名
        for overlay in overlays:
            canvas.delete_overlay(overlay)
        print(f"Removed overlay for item {index}")
        update_config_includes(file_name, 'remove')
    elif action == 'add':
        # 选中：添加蒙层并将文件名加入 includes
        x1, y1, x2, y2 = canvas.get_object_bbox(canvas.image_id)
        canvas.draw_rectangle_overlay(
            x1, y1, x2, y2,
            fill='green',
            alpha=.5,
            tags=(overlay_tag, 'overlay'),
            outline=''
        )
        print(f"Added overlay for item {index}")
        update_config_includes(file_name, 'add')

def handle_selection_lazy(event, index, file_name, cell_grid):
    """
    懒加载模式下的选中/反选处理函数
    :param event: Tkinter 事件
    :param index: 图像索引
    :param file_name: 文件名
    :param cell_grid: 所有 Canvas 单元格列表
    """
    canvas = cell_grid[index]
    file_name = os.path.basename(file_name)
    if not canvas.get_item_by_index(index):
        toggle_selection(canvas, index, file_name, 'add')
    else:
        toggle_selection(canvas, index, file_name, 'remove')

def initialize_selected_avatars(cell_grid, index, image_paths, loader):
    """
    启动时初始化已选中的头像文件
    :param cell_grid: 所有 Graph 对象列表
    :param index: 图片索引
    :param image_paths: 所有头像文件路径
    :param loader: 图像加载器实例
    """
    includes = get_includes()  # 使用缓存的 includes 列表
    # 检查索引是否有效
    if index < 0 or index >= len(image_paths):
        logging.warning(f"Invalid index {index} for image_paths")
        return

    path = image_paths[index]
    # 检查路径是否有效
    if not path or not os.path.exists(path):
        logging.warning(f"Invalid or non-existent path: {path}")
        return

    file_name = os.path.basename(path)
    key = file_name[:-4]
    if key in includes:
        # 直接从 cell_grid 列表中获取对应的 Graph 对象
        graph_canvas = cell_grid[index]
        # 确保图像已加载完成后再进行操作
        if loader.loaded_flags.get(index, False):
            # 使用 get_item_by_index 方法获取 Canvas 对象
            if not graph_canvas.get_item_by_index(index):
                toggle_selection(graph_canvas, index, file_name, 'add')

def setup_grid_layout_lazy(scrollable_frame, config_params, image_paths, loader):
    """Optimized grid layout with lazy loading and selection support"""

    def update_cell(index, photo, cell_grid):
        if index < len(cell_grid):
            canvas = cell_grid[index]
            # 如果还没有创建图像对象，则创建一个
            if not hasattr(canvas, 'image_id'):
                image_id = canvas.create_image(50, 50, image=photo)
                canvas.image_id = image_id  # 保存 ID 以便后续更新
            else:
                # 更新已有的图像
                canvas.itemconfig(canvas.image_id, image=photo)
            canvas.photo = photo  # 防止被垃圾回收
            loader.loaded_flags[index] = True

            # 启动时初始化已选中的头像文件
            initialize_selected_avatars(cell_grid, index, image_paths, loader)

    cell_grid = []
    for i, path in enumerate(image_paths):
        canvas = Graph(
            scrollable_frame,
            width=100,
            height=100,
            highlightthickness=0,
            bg="white"
        )
        canvas.grid(
            row=i // config_params.rows_per_column,
            column=i % config_params.columns,
            padx=config_params.padding_x,
            pady=config_params.padding_y,
            sticky="nsew"
        )
        cell_grid.append(canvas)

        # 创建点击处理器并绑定
        file_name = os.path.basename(path)
        handler = lambda e, idx=i, fn=file_name: handle_selection_lazy(e, idx, fn, cell_grid)
        canvas.bind("<Button-1>", handler)

    # 初始化滚动区域大小
    rows = (len(image_paths) + config_params.columns - 1) // config_params.columns
    total_height = rows * (100 + config_params.padding_y) + config_params.padding_y
    scrollable_frame.master.configure(scrollregion=(0, 0, 0, total_height))

    # 立即加载可见区域图像
    for i in range(config_params.rows_per_column * config_params.columns):
        if i < len(image_paths):
            loader.get_or_queue(image_paths[i], i, lambda idx, photo: update_cell(idx, photo, cell_grid))

    def on_scroll(*args):
        visible_start = scrollable_frame.winfo_y()
        visible_end = visible_start + scrollable_frame.winfo_height()

        for i, path in enumerate(image_paths):
            row = i // config_params.columns
            y_start = row * (100 + config_params.padding_y)
            y_end = y_start + 100

            if y_start <= visible_end + 300 and y_end >= visible_start - 300:
                if not loader.loaded_flags.get(i, False):
                    loader.get_or_queue(path, i, lambda idx, photo: update_cell(idx, photo, cell_grid))

    scrollable_frame.bind("<Configure>", lambda e: on_scroll())
    scrollable_frame.bind("<MouseWheel>", lambda e: on_scroll())

def setup_scroll_management(canvas):
    """设置滚动管理"""
    def on_mousewheel(event):
        if event.num == 4 or event.delta > 0:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            canvas.yview_scroll(1, "units")

    # 绑定鼠标滚轮事件
    canvas.bind_all("<MouseWheel>", on_mousewheel)  # Windows
    canvas.bind_all("<Button-4>", on_mousewheel)   # Linux (向上滚动)
    canvas.bind_all("<Button-5>", on_mousewheel)   # Linux (向下滚动)

def display_avatar_gui(base_wechat_dir):
    """使用 GUI 显示头像文件，支持后续接入懒加载"""
    root = Tk()
    root.title("WeChat 头像管理")

    # 1. 窗口配置
    center_window(root)

    # 2. 创建主容器
    canvas, scrollbar, scrollable_frame = create_main_container(root)

    # 3. 设置滚动行为
    setup_scroll_management(canvas)

    # 4. 获取头像路径
    avatar_files = find_avatar_files(base_wechat_dir)

    # 5. 加载图像并布局网格（预留懒加载扩展点）
    loader = ImageLoader(max_workers=4)
    setup_grid_layout_lazy(scrollable_frame, ConfigParams(), avatar_files, loader)
    # loaded_images = []
    # load_next_images(avatar_files, loaded_images, scrollable_frame, ConfigParams())

    root.mainloop()


def create_main_container(root):
    """创建主画布和滚动区域"""
    canvas = Canvas(root, bg="white")
    scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas, bg="white")

    # 配置滚动区域
    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", on_configure)

    # 嵌套结构
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # 布局
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return canvas, scrollbar, scrollable_frame

def load_next_images(avatar_files, loaded_images, scrollable_frame, config_params):
    """
    批量加载图像资源（可替换为懒加载策略）
    :param avatar_files: 图像路径列表
    :param loaded_images: 已加载的 (PhotoImage, filename) 列表
    :param scrollable_frame: 容器 Frame
    :param config_params: 网格配置参数
    """
    start_index = len(loaded_images)
    end_index = min(start_index + 100, len(avatar_files))

    for i in range(start_index, end_index):
        avatar_file = avatar_files[i]
        try:
            if not os.path.exists(avatar_file):
                print(f"文件不存在: {avatar_file}")
                continue
            if not avatar_file.lower().endswith(".jpg"):
                print(f"文件不是有效的 JPEG 图像: {avatar_file}")
                continue

            img = Image.open(avatar_file)
            img = img.resize((100, 100))
            photo = ImageTk.PhotoImage(img)
            loaded_images.append((photo, os.path.basename(avatar_file)))
        except Exception as e:
            print(f"无法加载图像文件: {avatar_file}, 错误: {e}")

    # 当前同步加载，未来可替换为懒加载实现
    # setup_grid_layout(scrollable_frame, config_params, loaded_images)

    # 继续异步加载
    if end_index < len(avatar_files):
        root = scrollable_frame.winfo_toplevel()
        root.after(100, lambda: load_next_images(avatar_files, loaded_images, scrollable_frame, config_params))

def main():
    """主程序"""
    try:
        home_dir = os.path.expanduser("~")
        # 修改: 将 base_wechat_dir 设置为可配置的变量
        base_wechat_dir = os.getenv("WECHAT_DIR", os.path.join(home_dir, "Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/"))
        
        if not os.path.exists(base_wechat_dir):
            print(f"未找到 WeChat 文件夹，请检查路径: {base_wechat_dir}")
            return
        
        while True:
            display_avatar_gui(base_wechat_dir)
    except Exception as e:
        logging.error(f"管理端启动失败: {e}", exc_info=True)
        print(f"管理端启动失败: {e}")

if __name__ == "__main__":
    main()
