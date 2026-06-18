import flet as ft
# 💥 關鍵差異：必須獨立引入這兩個外掛套件
import flet_permission_handler as fph
import flet_camera as fcam
import os

def main(page: ft.Page):
    page.title = "原生相機直連測試 (0.85版)"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # 1. 使用獨立套件建立權限處理器 (fph)
    ph = fph.PermissionHandler()
    page.overlay.append(ph)

    info_text = ft.Text("請點擊下方按鈕啟動相機...", size=18, color="blue", weight="bold")
    
    # 2. 使用獨立套件建立相機元件 (fcam)
    camera = fcam.Camera(
        expand=True,
        visible=False
    )
    
    camera_container = ft.Container(
        content=camera,
        expand=True,
        bgcolor="black",
        border_radius=10
    )

    async def open_camera(e):
        info_text.value = "嘗試要求權限並開啟相機中..."
        page.update()
        
        try:
            # 請求相機權限 (兼容不同的枚舉寫法避免當機)
            if hasattr(fph, "Permission"):
                await ph.request_permission(fph.Permission.CAMERA)
            else:
                await ph.request_permission(ft.PermissionType.CAMERA)
        except Exception as ex:
            print(f"權限詢問略過(電腦端常見): {ex}")
            
        camera.visible = True
        info_text.value = "相機已啟動！(電腦若無鏡頭將顯示黑畫面)"
        page.update()

    async def take_photo(e):
        save_path = os.path.join(os.getcwd(), "test_photo.png")
        try:
            # 送出拍照指令
            camera.take_picture(save_path)
            info_text.value = f"喀嚓！拍照指令已送出！"
        except Exception as ex:
            info_text.value = f"拍照發生錯誤: {ex}"
        page.update()

    page.add(
        info_text,
        camera_container,
        ft.Row([
            ft.ElevatedButton("1. 要求權限並開相機", on_click=open_camera, bgcolor="blue", color="white"),
            ft.ElevatedButton("2. 🔴 拍照", on_click=take_photo, bgcolor="red", color="white")
        ], alignment=ft.MainAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    ft.run(main)