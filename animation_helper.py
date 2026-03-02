from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup, QAbstractAnimation
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect, QDialog


class AnimatedDialogMixin:
    """
    Mixin class cho các dialog có animation.
    Sử dụng: class MyDialog(AnimatedDialogMixin, QDialog)
    Cung cấp phương thức dừng animation an toàn khi đóng dialog.
    """
    
    def _stop_animations(self):
        """Dừng tất cả animation để ngăn crash khi đóng dialog."""
        try:
            if hasattr(self, '_open_anim') and self._open_anim:
                self._open_anim.stop()
                self._open_anim = None
            if hasattr(self, '_fade_anim') and self._fade_anim:
                self._fade_anim.stop()
                self._fade_anim = None
        except RuntimeError:
            # C++ object đã bị xóa, bỏ qua
            pass
            
        # Gỡ graphics effect nếu còn
        if isinstance(self, QWidget):
            self.setGraphicsEffect(None)
    
    def reject(self):
        self._stop_animations()
        super().reject()
    
    def accept(self):
        self._stop_animations()
        super().accept()

class AnimationHelper:
    @staticmethod
    def fade_in(widget: QWidget, duration=400, easing=QEasingCurve.Type.OutCubic):
        """
        Tạo hiệu ứng Fade-in cho widget.
        Quan trọng: Tự động gỡ bỏ QGraphicsOpacityEffect sau khi hoàn tất để tránh lỗi hiển thị.
        """
        if not widget: return
        
        # Reset opacity effect nếu đã có
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        anim = QPropertyAnimation(effect, b"opacity", widget)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(duration)
        anim.setEasingCurve(easing)
        
        # --- FIX: Clean up effect to restore native rendering ---
        def on_finished():
            widget.setGraphicsEffect(None)
            if hasattr(widget, '_fade_anim'):
                widget._fade_anim = None
            
        anim.finished.connect(on_finished)
        # -------------------------------------------------------
        
        # Giữ reference để animation không bị garbage collected ngay lập tức
        widget._fade_anim = anim 
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    @staticmethod
    def shake_widget(widget: QWidget):
        """
        Hiệu ứng rung lắc nhẹ để báo lỗi.
        """
        if not widget: return
        
        anim = QPropertyAnimation(widget, b"pos", widget)
        pos = widget.pos()
        anim.setDuration(300)
        anim.setLoopCount(1)
        
        # Keyframes
        anim.setKeyValueAt(0, pos)
        anim.setKeyValueAt(0.1, QPoint(pos.x() + 5, pos.y()))
        anim.setKeyValueAt(0.2, QPoint(pos.x() - 5, pos.y()))
        anim.setKeyValueAt(0.3, QPoint(pos.x() + 5, pos.y()))
        anim.setKeyValueAt(0.4, QPoint(pos.x() - 5, pos.y()))
        anim.setKeyValueAt(0.5, QPoint(pos.x(), pos.y()))
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        def on_finished():
             if hasattr(widget, '_shake_anim'):
                widget._shake_anim = None

        anim.finished.connect(on_finished)
        
        widget._shake_anim = anim
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    @staticmethod
    def animate_dialog_open(dialog: QWidget):
        """
        Hiệu ứng mở Dialog: Slide nhẹ từ dưới lên + Fade in.
        Quan trọng: Tự động gỡ bỏ QGraphicsOpacityEffect sau khi hoàn tất.
        """
        if not dialog: return

        effect = QGraphicsOpacityEffect(dialog)
        dialog.setGraphicsEffect(effect)
        
        # Lấy geometry hiện tại (đã được center bởi Qt)
        end_geo = dialog.geometry()
        start_geo = QPoint(end_geo.x(), end_geo.y() + 30) # Bắt đầu thấp hơn 30px
        
        group = QParallelAnimationGroup(dialog)
        
        # 1. Fade In
        anim_op = QPropertyAnimation(effect, b"opacity")
        anim_op.setStartValue(0.0)
        anim_op.setEndValue(1.0)
        anim_op.setDuration(300)
        anim_op.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 2. Slide Up (Dùng pos thay vì geometry để an toàn hơn)
        anim_pos = QPropertyAnimation(dialog, b"pos")
        anim_pos.setStartValue(start_geo)
        anim_pos.setEndValue(end_geo.topLeft())
        anim_pos.setDuration(300)
        anim_pos.setEasingCurve(QEasingCurve.Type.OutBack) # Hiệu ứng nảy nhẹ
        
        group.addAnimation(anim_op)
        group.addAnimation(anim_pos)
        
        # --- FIX: Clean up effect ---
        def on_finished():
            dialog.setGraphicsEffect(None)
            if hasattr(dialog, '_open_anim'):
                dialog._open_anim = None
        
        group.finished.connect(on_finished)
        # ----------------------------
        
        dialog._open_anim = group
        group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)