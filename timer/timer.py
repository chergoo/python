import datetime
import json
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, ListProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase

# 注册支持中文的字体（请确保 SimHei.ttf 文件在项目目录中）
LabelBase.register(name="SimHei", fn_regular="SimHei.ttf")

# KV 语言定义界面布局
kv = '''
<SubscriptionItem>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(40)
    padding: dp(5)
    canvas.before:
        Color:
            rgba: root.bg_color
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        text: root.name
        font_name: "SimHei"
        size_hint_x: 0.1
    Label:
        text: root.next_date
        font_name: "SimHei"
        size_hint_x: 0.1
    Label:
        text: str(root.countdown)
        font_name: "SimHei"
        size_hint_x: 0.1
    Label:
        text: str(root.amount)
        font_name: "SimHei"
        size_hint_x: 0.1
    Label:
        text: root.remarks
        font_name: "SimHei"
        size_hint_x: 0.1
    Button:
        text: '修改'
        font_name: "SimHei"
        size_hint_x: 0.1
        on_release: root.edit_subscription()
    Button:
        text: '删除'
        font_name: "SimHei"
        size_hint_x: 0.1
        on_release: root.delete_subscription()
    Button:
        text: '续费'
        font_name: "SimHei"
        size_hint_x: 0.1
        on_release: root.renew_subscription()

<SubscriptionTracker>:
    orientation: 'vertical'
    BoxLayout:
        size_hint_y: None
        height: dp(40)
        padding: dp(5)
        spacing: dp(5)
        Label:
            text: '名称'
            font_name: "SimHei"
            size_hint_x: 0.1
        Label:
            text: '续费日期'
            font_name: "SimHei"
            size_hint_x: 0.1
        Label:
            text: '倒计时(天)'
            font_name: "SimHei"
            size_hint_x: 0.1
        Label:
            text: '金额'
            font_name: "SimHei"
            size_hint_x: 0.1
        Label:
            text: '备注'
            font_name: "SimHei"
            size_hint_x: 0.1
        Label:
            text: ''
            size_hint_x: 0.1
        Label:
            text: ''
            size_hint_x: 0.1
        Label:
            text: ''
            size_hint_x: 0.1
    RecycleView:
        id: rv
        viewclass: 'SubscriptionItem'
        RecycleBoxLayout:
            default_size: None, dp(40)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
    Button:
        text: '添加订阅'
        font_name: "SimHei"
        size_hint_y: None
        height: dp(40)
        on_release: root.open_add_popup()

<AddSubscriptionPopup>:
    title: '添加订阅'
    font_name: "SimHei"
    size_hint: 0.8, 0.8
    auto_dismiss: False
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(10)
        TextInput:
            id: name_input
            hint_text: '订阅名称'
            multiline: False
            font_name: "SimHei"
        TextInput:
            id: date_input
            hint_text: '开始日期 (YYYY-MM-DD)'
            multiline: False
            font_name: "SimHei"
        TextInput:
            id: cycle_input
            hint_text: '续费周期 (天)'
            multiline: False
            input_filter: 'int'
            font_name: "SimHei"
        TextInput:
            id: amount_input
            hint_text: '金额'
            multiline: False
            input_filter: 'float'
            font_name: "SimHei"
        TextInput:
            id: remarks_input
            hint_text: '备注'
            multiline: False
            font_name: "SimHei"
        BoxLayout:
            size_hint_y: None
            height: dp(40)
            spacing: dp(10)
            Button:
                text: '取消'
                font_name: "SimHei"
                on_release: root.dismiss()
            Button:
                text: '确定'
                font_name: "SimHei"
                on_release: root.add_subscription(name_input.text, date_input.text, cycle_input.text, amount_input.text, remarks_input.text)

<EditSubscriptionPopup>:
    title: '修改订阅'
    font_name: "SimHei"
    size_hint: 0.8, 0.8
    auto_dismiss: False
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(10)
        TextInput:
            id: name_input
            hint_text: '订阅名称'
            multiline: False
            font_name: "SimHei"
        TextInput:
            id: date_input
            hint_text: '开始日期 (YYYY-MM-DD)'
            multiline: False
            font_name: "SimHei"
        TextInput:
            id: cycle_input
            hint_text: '续费周期 (天)'
            multiline: False
            input_filter: 'int'
            font_name: "SimHei"
        TextInput:
            id: amount_input
            hint_text: '金额'
            multiline: False
            input_filter: 'float'
            font_name: "SimHei"
        TextInput:
            id: remarks_input
            hint_text: '备注'
            multiline: False
            font_name: "SimHei"
        BoxLayout:
            size_hint_y: None
            height: dp(40)
            spacing: dp(10)
            Button:
                text: '取消'
                font_name: "SimHei"
                on_release: root.dismiss()
            Button:
                text: '确定'
                font_name: "SimHei"
                on_release: root.save_subscription(name_input.text, date_input.text, cycle_input.text, amount_input.text, remarks_input.text)
'''

Builder.load_string(kv)

# -------------------------------
# 业务逻辑部分

class Subscription:
    """
    订阅项目数据模型
    """
    def __init__(self, name, start_date, renewal_cycle, amount, remarks):
        """
        :param name: 订阅名称
        :param start_date: 开始日期（datetime.date 对象）
        :param renewal_cycle: 续费周期（天数，int）
        :param amount: 金额（float）
        :param remarks: 备注
        """
        self.name = name
        self.start_date = start_date
        self.renewal_cycle = renewal_cycle
        self.amount = amount
        self.remarks = remarks

    def next_renewal_date(self):
        """
        根据开始日期和续费周期计算下一次续费日期，若开始日期在过去，则不断累加周期直至 >= 今天
        """
        today = datetime.date.today()
        period = datetime.timedelta(days=self.renewal_cycle)
        next_date = self.start_date    
        next_date += period
        return next_date

    def days_until_renewal(self):
        """
        计算距离下一次续费的天数
        """
        return (self.next_renewal_date() - datetime.date.today()).days

    def to_dict(self):
        """
        将订阅对象转换为字典
        """
        return {
            'name': self.name,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'renewal_cycle': self.renewal_cycle,
            'amount': self.amount,
            'remarks': self.remarks
        }

    @staticmethod
    def from_dict(data):
        """
        从字典创建订阅对象
        """
        return Subscription(
            name=data['name'],
            start_date=datetime.datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            renewal_cycle=data['renewal_cycle'],
            amount=data['amount'],
            remarks=data['remarks']
        )

class SubscriptionItem(BoxLayout):
    """
    RecycleView 的单个订阅项
    """
    name = StringProperty('')
    next_date = StringProperty('')
    countdown = NumericProperty(0)
    amount = NumericProperty(0)
    remarks = StringProperty('')
    bg_color = ListProperty([1, 1, 1, 1])
    subscription = ObjectProperty(None)  # 这里添加 Subscription 对象的引用

    def edit_subscription(self):
        """
        打开修改订阅的弹出窗口
        """
        if not self.subscription:
            print("错误：无法编辑，因为缺少 Subscription 数据")
            return
        
        popup = EditSubscriptionPopup(tracker=self.parent.parent.parent, subscription=self.subscription)
        popup.open()

    def delete_subscription(self):
            """
            调用 SubscriptionTracker 的删除方法
            """
            if self.subscription:
                self.parent.parent.parent.delete_subscription(self.subscription)

    def renew_subscription(self):
        if self.subscription:
            today = datetime.date.today()
            next_date = self.subscription.next_renewal_date()
            countdown = (next_date - today).days
            print(f"Today: {today}, Next Date: {next_date}, Countdown: {countdown}")
            if countdown > 0:
                next_date += datetime.timedelta(days=countdown)
            else:
                next_date = today 
            print(f"New Next Date: {next_date}")
            self.subscription.start_date = next_date
            self.parent.parent.parent.update_rv()
            self.parent.parent.parent.save_subscriptions()  # 保存订阅数据

class AddSubscriptionPopup(Popup):
    """
    添加订阅的弹出窗口
    """
    tracker = ObjectProperty(None)  # 保存对主界面 SubscriptionTracker 的引用

    def add_subscription(self, name, date_str, cycle_str, amount_str, remarks):
        """
        获取表单数据并尝试添加订阅
        """
        try:
            # 解析日期（格式要求 YYYY-MM-DD）
            start_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            renewal_cycle = int(cycle_str)
            amount = float(amount_str)
        except Exception as e:
            print("输入错误：", e)
            return  # 如果输入错误，可进一步扩展为弹出错误提示
        # 创建 Subscription 对象
        sub = Subscription(name, start_date, renewal_cycle, amount, remarks)
        self.tracker.add_subscription(sub)
        self.dismiss()

class EditSubscriptionPopup(Popup):
    """
    修改订阅的弹出窗口
    """
    tracker = ObjectProperty(None)  # 保存对主界面 SubscriptionTracker 的引用
    subscription = ObjectProperty(None)  # 保存当前订阅项的引用

    def on_open(self):
        """
        弹出窗口打开时，初始化表单数据
        """
        self.ids.name_input.text = self.subscription.name
        self.ids.date_input.text = self.subscription.start_date.strftime('%Y-%m-%d')
        self.ids.cycle_input.text = str(self.subscription.renewal_cycle)
        self.ids.amount_input.text = str(self.subscription.amount)
        self.ids.remarks_input.text = self.subscription.remarks

    def save_subscription(self, name, date_str, cycle_str, amount_str, remarks):
        """
        保存修改后的订阅数据
        """
        try:
            # 解析日期（格式要求 YYYY-MM-DD）
            start_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            renewal_cycle = int(cycle_str)
            amount = float(amount_str)
        except Exception as e:
            print("输入错误：", e)
            return  # 如果输入错误，可进一步扩展为弹出错误提示
        # 更新 Subscription 对象
        self.subscription.name = name
        self.subscription.start_date = start_date
        self.subscription.renewal_cycle = renewal_cycle
        self.subscription.amount = amount
        self.subscription.remarks = remarks
        self.tracker.update_rv()
        self.tracker.save_subscriptions()  # 保存订阅数据
        self.dismiss()

class SubscriptionTracker(BoxLayout):
    """
    主界面：展示订阅列表和“添加订阅”按钮
    """
    subscriptions = ListProperty([])  # 订阅列表

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subscriptions = self.load_subscriptions()  # 加载订阅数据
        self.update_rv()

    def add_subscription(self, sub):
        """
        添加订阅后，对列表按照下一次续费日期排序，并更新显示
        """
        self.subscriptions.append(sub)
        self.subscriptions.sort(key=lambda x: x.next_renewal_date())
        self.update_rv()
        self.save_subscriptions()  # 保存订阅数据

    def delete_subscription(self, subscription):
        """
        删除订阅并更新 RecycleView
        """
        if subscription in self.subscriptions:
            self.subscriptions.remove(subscription)
            self.update_rv()
            self.save_subscriptions()  # 保存订阅数据

    def update_rv(self):
        """
        更新 RecycleView 数据，计算每个项目的下一次续费日期和倒计时，并设置背景颜色
        """
        data = []
        for sub in self.subscriptions:
            next_date = sub.next_renewal_date()
            countdown = (next_date - datetime.date.today()).days
            # 倒计时0天内显示红色，5天内显示粉色
            if countdown <= 0:
                bg_color = [1, 0, 0, 1]  # 红色
            elif countdown <= 5:
                bg_color = [1, 0.7, 0.7, 1]  # 粉色
            else:
                bg_color = [0, 0.7, 0, 1]  # 白色

            data.append({
                'name': sub.name,
                'next_date': next_date.strftime('%Y-%m-%d'),
                'countdown': countdown,
                'amount': sub.amount,
                'remarks': sub.remarks,
                'bg_color': bg_color,
                'subscription': sub  # 这里把 Subscription 对象传递进去，避免 AttributeError
            })

        self.ids.rv.data = data

    def save_subscriptions(self):
        """
        将订阅数据保存到 JSON 文件
        """
        data = [sub.to_dict() for sub in self.subscriptions]
        with open('subscriptions.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_subscriptions(self):
        """
        从 JSON 文件加载订阅数据
        """
        try:
            with open('subscriptions.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Subscription.from_dict(item) for item in data]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print("JSON 文件格式错误")
            return []

    def open_add_popup(self):
        """
        打开添加订阅的弹出窗口
        """
        popup = AddSubscriptionPopup(tracker=self)
        popup.open()

class SubscriptionApp(App):
    def build(self):
        return SubscriptionTracker()

if __name__ == '__main__':
    SubscriptionApp().run()