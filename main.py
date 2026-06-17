import os
import glob
from datetime import datetime
import flet as ft

def main(page: ft.Page):
    # 📱 1. 基本設定
    page.title = "智慧巡檢拍照 App V1"
    page.padding = 10

    # 📂 2. 資料夾與記憶體初始化
    today_str = datetime.now().strftime("%Y%m%d")
    save_dir = os.path.join(os.getcwd(), today_str)
    os.makedirs(save_dir, exist_ok=True) 

    current_step = 1  
    group_counter = 1 
    captured_photos = ["#e1e1e1", "#e1e1e1", "#e1e1e1", "#e1e1e1"]
    previous_photos = None 

    # 🔍 開機自動掃描機制
    existing_files = glob.glob(os.path.join(save_dir, "*_4.jpg"))
    if existing_files:
        max_group = 0
        for f in existing_files:
            try:
                filename = os.path.basename(f)
                g_num = int(filename.split('_')[0])
                if g_num > max_group:
                    max_group = g_num
            except:
                pass
        
        if max_group > 0:
            group_counter = max_group + 1
            previous_photos = ["green", "green", "blue", "purple"] 
            print(f"🔥 [系統偵測] 發現今日已完成 {max_group} 組，自動從第 {group_counter} 組繼續！")

    step_titles = {
        1: "【步驟 1 / 4】請拍攝：遠照（整體環境）",
        2: "【步驟 2 / 4】請拍攝：近照（異常點特寫）",
        3: "【步驟 3 / 4】請拍攝：設備編號 (請對準標籤)",
        4: "【步驟 4 / 4】請拍攝：異常周遭的設備"
    }
    retake_target = 0 

    # 🎨 3. 建立畫面的 UI 元件
    info_text = ft.Text(value="", size=14, weight="bold", color="blue", text_align="center")
    
    camera_view = ft.Container(
        width=340, height=400, bgcolor="black", border_radius=10, alignment=ft.Alignment(0, 0),
        content=ft.Container(
            width=280, height=320,
            border=ft.Border(top=ft.BorderSide(2, "white"), right=ft.BorderSide(2, "white"), bottom=ft.BorderSide(2, "white"), left=ft.BorderSide(2, "white")),
            alignment=ft.Alignment(0, 0), content=ft.Text("📷 相機鏡頭畫面模擬區域", color="white", size=12)
        )
    )

    # 🔄 畫面更新邏輯
    def update_camera_ui():
        prefix = f"(第 {group_counter:03d} 組) "
        info_text.value = f"🔥 [單獨重拍中] {step_titles[retake_target]}" if retake_target > 0 else prefix + step_titles[current_step]
        
        if retake_target == 0 and previous_photos is not None and current_step in [3, 4]:
            reuse_btn.visible = True
            # 💥 修正點：將長長的一串字，直接精簡為「♻️ 沿用上一組」
            reuse_btn.content.value = "♻️ 沿用上一組"
        else:
            reuse_btn.visible = False
        page.update()

    # 📸 4. 快門按鈕點擊邏輯
    def take_photo_click(e):
        nonlocal current_step, retake_target
        color_pool = ["orange", "green", "blue", "purple"]
        
        if retake_target > 0:
            captured_photos[retake_target - 1] = color_pool[retake_target - 1]
            retake_target = 0 
            show_review_panel() 
        else:
            captured_photos[current_step - 1] = color_pool[current_step - 1]
            if current_step < 4:
                current_step += 1
                update_camera_ui()
            else:
                show_review_panel()

    def reuse_photo_click(e):
        nonlocal current_step
        captured_photos[current_step - 1] = previous_photos[current_step - 1]
        if current_step < 4:
            current_step += 1
            update_camera_ui()
        else:
            show_review_panel()

    shutter_btn = ft.Container(
        content=ft.Text("🔴 點擊拍攝快門", color="white", weight="bold", size=16),
        bgcolor="red", width=250, height=50, border_radius=25, alignment=ft.Alignment(0, 0), on_click=take_photo_click
    )
    reuse_btn = ft.Container(
        content=ft.Text("", color="white", size=14, weight="bold"), # 字體稍微放大加粗一點
        bgcolor="blue", width=250, height=40, border_radius=10, alignment=ft.Alignment(0, 0), on_click=reuse_photo_click, visible=False
    )
    camera_controls = ft.Column([shutter_btn, reuse_btn], alignment="center", horizontal_alignment="center", spacing=10)

    # 🧩 5. 2x2 綜合確認面板排版
    def on_single_box_click(e, box_idx):
        nonlocal retake_target
        retake_target = box_idx
        page.controls.clear()
        page.add(info_text, camera_view, camera_controls)
        update_camera_ui()

    def save_and_next_group(e):
        nonlocal current_step, group_counter, previous_photos
        
        for i in range(1, 5):
            filepath = os.path.join(save_dir, f"{group_counter:03d}_{i}.jpg")
            with open(filepath, 'w') as f:
                f.write("這是一張假照片") 
                
        previous_photos = list(captured_photos) 
        print(f"✅ 成功存入實體資料夾 {save_dir}！")
        
        current_step = 1
        group_counter += 1
        
        page.controls.clear()
        page.add(info_text, camera_view, camera_controls)
        update_camera_ui()

    def show_review_panel():
        info_text.value = f"🔎 第 {group_counter:03d} 組 2x2 畫面確認 (若有模糊可點擊單獨重拍)"
        grid = ft.Column([
            ft.Row([
                ft.Container(content=ft.Text("1.遠照\n(點擊重拍)", text_align="center", color="black"), bgcolor=captured_photos[0], width=160, height=130, border_radius=5, alignment=ft.Alignment(0, 0), on_click=lambda e: on_single_box_click(e, 1)),
                ft.Container(content=ft.Text("2.近照\n(點擊重拍)", text_align="center", color="black"), bgcolor=captured_photos[1], width=160, height=130, border_radius=5, alignment=ft.Alignment(0, 0), on_click=lambda e: on_single_box_click(e, 2)),
            ], alignment="center"), 
            ft.Row([
                ft.Container(content=ft.Text("3.編號\n(點擊重拍)", text_align="center", color="black"), bgcolor=captured_photos[2], width=160, height=130, border_radius=5, alignment=ft.Alignment(0, 0), on_click=lambda e: on_single_box_click(e, 3)),
                ft.Container(content=ft.Text("4.周遭\n(點擊重拍)", text_align="center", color="black"), bgcolor=captured_photos[3], width=160, height=130, border_radius=5, alignment=ft.Alignment(0, 0), on_click=lambda e: on_single_box_click(e, 4)),
            ], alignment="center"), 
        ], spacing=10)

        action_row = ft.Row([
            ft.Container(content=ft.Text("❌ 全部重拍", color="white", weight="bold"), bgcolor="grey", width=120, height=40, border_radius=5, alignment=ft.Alignment(0, 0), on_click=lambda e: restart_current_group()), 
            ft.Container(content=ft.Text("✔ 確認儲存", color="white", weight="bold"), bgcolor="green", width=120, height=40, border_radius=5, alignment=ft.Alignment(0, 0), on_click=save_and_next_group)
        ], alignment="center", spacing=20)

        page.controls.clear()
        page.add(info_text, grid, ft.Divider(height=20), action_row)
        page.update()

    def restart_current_group():
        nonlocal current_step, retake_target
        current_step = 1
        retake_target = 0
        page.controls.clear()
        page.add(info_text, camera_view, camera_controls)
        update_camera_ui()

    # 🚀 6. 啟動首頁
    page.add(info_text, camera_view, camera_controls)
    update_camera_ui()

try:
    ft.run(main)
except AttributeError:
    ft.app(target=main)