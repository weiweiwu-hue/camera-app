import flet as ft

def main(page: ft.Page):
    # 📱 1. 基礎設定
    page.title = "智慧巡檢 App - 乾淨重啟版"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 10

    # ==========================================
    # 📷 2. 核心元件初始化 (最新 Service 架構)
    # ==========================================
    file_picker = ft.FilePicker()
    
    # 確保 FilePicker 作為背景服務運行，徹底避開 Unknown control 紅框！
    if hasattr(page, "services"):
        page.services.append(file_picker)
    else:
        page.overlay.append(file_picker)
    
    # 📂 3. 狀態變數
    current_step = 1  
    group_counter = 1 
    captured_photos = ["", "", "", ""]
    previous_photos = None 
    retake_target = 0 
    
    step_titles = {
        1: "【步驟 1 / 4】拍攝：遠照（整體環境）",
        2: "【步驟 2 / 4】拍攝：近照（異常特寫）",
        3: "【步驟 3 / 4】拍攝：設備編號",
        4: "【步驟 4 / 4】拍攝：周遭設備"
    }

    root_view = ft.Container(expand=True)
    info_text = ft.Text(value="", size=18, weight="bold", color="blue", text_align="center")
    notch_spacer = ft.Container(height=40)

    # ==========================================
    # 🧠 5. 核心 UI 邏輯
    # ==========================================
    def update_camera_ui():
        prefix = f"(第 {group_counter:03d} 組)\n"
        info_text.value = f"🔥 [單獨重拍中]\n{step_titles[retake_target]}" if retake_target > 0 else prefix + step_titles[current_step]
        
        if retake_target == 0 and previous_photos is not None and current_step in [3, 4]:
            reuse_btn.visible = True
        else:
            reuse_btn.visible = False
        page.update()

    # 💥 非同步呼叫相機，絕不卡死
    async def take_photo_click(e):
        try:
            files = await file_picker.pick_files(allow_multiple=False, file_type="image")
            
            nonlocal current_step, retake_target
            if files and len(files) > 0:
                photo_path = files[0].path
                if retake_target > 0:
                    captured_photos[retake_target - 1] = photo_path
                    retake_target = 0 
                    switch_to_review() 
                else:
                    captured_photos[current_step - 1] = photo_path
                    if current_step < 4:
                        current_step += 1
                        update_camera_ui()
                    else:
                        switch_to_review()
        except Exception as ex:
            print(f"呼叫相機異常: {ex}")

    def reuse_photo_click(e):
        nonlocal current_step
        captured_photos[current_step - 1] = previous_photos[current_step - 1]
        if current_step < 4:
            current_step += 1
            update_camera_ui()
        else:
            switch_to_review()

    # --- 畫面佈局：相機首頁 ---
    camera_view_box = ft.Container(
        expand=True, bgcolor="black", border_radius=10, alignment=ft.Alignment(0, 0),
        content=ft.Container(
            expand=True, margin=10,
            border=ft.Border(
                top=ft.BorderSide(2, "white"), right=ft.BorderSide(2, "white"), 
                bottom=ft.BorderSide(2, "white"), left=ft.BorderSide(2, "white")
            ),
            alignment=ft.Alignment(0, 0), 
            content=ft.Text("📷\n請點擊下方按鈕啟動相機/相簿", color="white", size=16, text_align="center")
        )
    )

    shutter_btn = ft.Container(
        content=ft.Text("🔴 點擊啟動相機", color="white", weight="bold", size=18),
        bgcolor="red", width=250, height=60, border_radius=30, alignment=ft.Alignment(0, 0), 
        on_click=take_photo_click
    )
    
    reuse_btn = ft.Container(
        content=ft.Text("♻️ 沿用上一組", color="white", size=14, weight="bold"), 
        bgcolor="blue", width=250, height=40, border_radius=10, alignment=ft.Alignment(0, 0), 
        on_click=reuse_photo_click, visible=False
    )
    
    camera_controls = ft.Column([shutter_btn, reuse_btn], alignment="center", horizontal_alignment="center", spacing=10)

    main_layout = ft.Column([
        notch_spacer, info_text, camera_view_box, camera_controls
    ], expand=True, horizontal_alignment="center", spacing=15)

    # --- 畫面佈局：確認頁面 ---
    def on_single_box_click(e, box_idx):
        nonlocal retake_target
        retake_target = box_idx
        switch_to_camera()

    def save_and_next_group(e):
        nonlocal current_step, group_counter, previous_photos
        previous_photos = list(captured_photos) 
        for i in range(4):
            captured_photos[i] = ""
        current_step = 1
        group_counter += 1
        switch_to_camera()

    def create_preview_box(idx, title):
        box_content = ft.Image(src=captured_photos[idx-1], fit="cover") if captured_photos[idx-1] != "" else ft.Text(title, text_align="center", color="black")
        return ft.Container(
            content=box_content, bgcolor="#e1e1e1", expand=1, height=150, border_radius=5, alignment=ft.Alignment(0, 0), 
            on_click=lambda e: on_single_box_click(e, idx)
        )

    def restart_current_group(e):
        nonlocal current_step, retake_target
        current_step = 1
        retake_target = 0
        for i in range(4):
            captured_photos[i] = ""
        switch_to_camera()

    def switch_to_camera():
        root_view.content = main_layout
        update_camera_ui()

    def switch_to_review():
        info_text.value = f"🔎 第 {group_counter:03d} 組確認 (點擊單格重拍)"
        grid = ft.Column([
            ft.Row([create_preview_box(1, "1.遠照\n(重拍)"), create_preview_box(2, "2.近照\n(重拍)")], alignment="center", expand=True), 
            ft.Row([create_preview_box(3, "3.編號\n(重拍)"), create_preview_box(4, "4.周遭\n(重拍)")], alignment="center", expand=True), 
        ], spacing=10, expand=True)

        action_row = ft.Row([
            ft.Container(content=ft.Text("❌ 全部重拍", color="white", weight="bold"), bgcolor="grey", expand=1, height=50, border_radius=5, alignment=ft.Alignment(0, 0), on_click=restart_current_group), 
            ft.Container(content=ft.Text("✔ 確認儲存", color="white", weight="bold"), bgcolor="green", expand=1, height=50, border_radius=5, alignment=ft.Alignment(0, 0), on_click=save_and_next_group)
        ], alignment="center", spacing=15)

        review_layout = ft.Column([notch_spacer, info_text, grid, ft.Divider(height=10), action_row], expand=True, horizontal_alignment="center")
        
        root_view.content = review_layout
        page.update()

    page.add(root_view)
    switch_to_camera()

if __name__ == "__main__":
    ft.run(main)