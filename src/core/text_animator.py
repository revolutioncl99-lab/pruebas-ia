"""Sistema de texto animado usando filtros FFmpeg drawtext."""
from __future__ import annotations

import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any


class TextAnimator:
    """Genera clips de texto animado con canal alpha usando FFmpeg."""

    ANIMATIONS: dict[str, dict[str, Any]] = {
        # --- Entrada ---
        "fade_in": {
            "type": "entrada",
            "duration": 0.5,
            "description": "Aparece gradualmente",
        },
        "slide_bottom": {
            "type": "entrada",
            "duration": 0.4,
            "description": "Entra desde abajo",
        },
        "slide_top": {
            "type": "entrada",
            "duration": 0.4,
            "description": "Entra desde arriba",
        },
        "slide_left": {
            "type": "entrada",
            "duration": 0.35,
            "description": "Entra desde la izquierda",
        },
        "slide_right": {
            "type": "entrada",
            "duration": 0.35,
            "description": "Entra desde la derecha",
        },
        "zoom_in": {
            "type": "entrada",
            "duration": 0.3,
            "description": "Crece desde el centro",
        },
        "typewriter": {
            "type": "entrada",
            "duration": "auto",
            "description": "Revela letra a letra",
        },
        "bounce": {
            "type": "entrada",
            "duration": 0.6,
            "description": "Cae y rebota",
        },
        "glitch_in": {
            "type": "entrada",
            "duration": 0.3,
            "description": "Aparece con efecto glitch",
        },
        # --- Salida ---
        "fade_out": {
            "type": "salida",
            "duration": 0.4,
            "description": "Desaparece gradualmente",
        },
        "slide_out_bottom": {
            "type": "salida",
            "duration": 0.35,
            "description": "Sale hacia abajo",
        },
        "zoom_out": {
            "type": "salida",
            "duration": 0.3,
            "description": "Se encoge hasta desaparecer",
        },
        # --- Loop continuo ---
        "pulse": {
            "type": "loop",
            "description": "Pulsa suavemente",
        },
        "shake": {
            "type": "loop",
            "description": "Vibra horizontalmente",
        },
        "wave": {
            "type": "loop",
            "description": "Letras en ola",
        },
        "none": {
            "type": "entrada",
            "duration": 0.0,
            "description": "Sin animación",
        },
    }

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def generate_text_clip(
        self,
        text: str,
        duration: float,
        animation_in: str,
        animation_out: str,
        style: dict,
        resolution: tuple[int, int] = (1920, 1080),
    ) -> str:
        """
        Genera un clip MP4 con fondo transparente (yuva420p) con el texto animado.
        Retorna el path al archivo generado en /tmp/.
        """
        W, H = resolution
        out_path = str(Path(tempfile.gettempdir()) / f"text_{uuid.uuid4().hex[:8]}.mov")

        font_path = self._resolve_font(style.get("font", "Arial"))
        font_size = style.get("size", 56)
        color = style.get("color", "#FFFFFF")
        outline_color = style.get("outline_color", "#000000")
        outline_width = style.get("outline_width", 2)

        # Posición base centrada
        x_base = f"(w-text_w)/2"
        y_base = f"(h-text_h)/2"

        x_expr, y_expr, alpha_expr = self._build_animation_exprs(
            animation_in, animation_out, duration, W, H, x_base, y_base,
            style.get("position", "center"),
        )

        safe_text = text.replace("'", "\\'").replace(":", "\\:")
        drawtext = (
            f"drawtext=fontfile={font_path}"
            f":text='{safe_text}'"
            f":fontsize={font_size}"
            f":fontcolor={color}"
            f":bordercolor={outline_color}"
            f":borderw={outline_width}"
            f":x={x_expr}:y={y_expr}"
            f":alpha='{alpha_expr}'"
        )

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=0x00000000:size={W}x{H}:rate=30",
            "-t", str(duration),
            "-vf", drawtext,
            "-c:v", "qtrle",
            "-pix_fmt", "argb",
            out_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(
                f"FFmpeg falló al generar clip de texto: {result.stderr[:400]}"
            )
        return out_path

    def build_title_sequence(self, lines: list[dict]) -> str:
        """
        Genera una secuencia de títulos animados concatenados.

        lines = [{"text": str, "start": float, "duration": float,
                  "anim_in": str, "anim_out": str, "style": dict}]
        Retorna path al video final.
        """
        clip_paths: list[str] = []
        for item in lines:
            path = self.generate_text_clip(
                text=item["text"],
                duration=item["duration"],
                animation_in=item.get("anim_in", "fade_in"),
                animation_out=item.get("anim_out", "fade_out"),
                style=item.get("style", {}),
            )
            clip_paths.append(path)

        out_path = str(Path(tempfile.gettempdir()) / f"seq_{uuid.uuid4().hex[:8]}.mov")
        self._concat_clips(clip_paths, out_path)
        for p in clip_paths:
            Path(p).unlink(missing_ok=True)
        return out_path

    # ------------------------------------------------------------------
    # Construcción de expresiones de animación
    # ------------------------------------------------------------------

    def _build_animation_exprs(
        self,
        anim_in: str,
        anim_out: str,
        duration: float,
        W: int,
        H: int,
        x_base: str,
        y_base: str,
        position: str = "center",
    ) -> tuple[str, str, str]:
        """Devuelve (x_expr, y_expr, alpha_expr) combinando entrada y salida."""
        x_expr = self._position_x(position, W)
        y_expr = self._position_y(position, H)
        alpha_expr = "1"

        in_dur = self._anim_duration(anim_in, duration)
        out_dur = self._anim_duration(anim_out, duration)

        # Alpha entrada
        alpha_in = "1"
        if anim_in == "fade_in" and in_dur > 0:
            alpha_in = f"if(lt(t,{in_dur:.3f}),t/{in_dur:.3f},1)"
        elif anim_in == "glitch_in" and in_dur > 0:
            alpha_in = f"if(lt(t,{in_dur:.3f}),floor(t/{in_dur:.3f}*4)/4,1)"

        # Alpha salida
        alpha_out = "1"
        out_start = duration - out_dur
        if anim_out == "fade_out" and out_dur > 0 and out_start > 0:
            alpha_out = f"if(gt(t,{out_start:.3f}),({duration:.3f}-t)/{out_dur:.3f},1)"
        elif anim_out == "zoom_out" and out_dur > 0 and out_start > 0:
            alpha_out = f"if(gt(t,{out_start:.3f}),({duration:.3f}-t)/{out_dur:.3f},1)"

        # Combinar alphas
        if alpha_in != "1" and alpha_out != "1":
            alpha_expr = f"min({alpha_in},{alpha_out})"
        elif alpha_in != "1":
            alpha_expr = alpha_in
        elif alpha_out != "1":
            alpha_expr = alpha_out

        # Y entrada (slides verticales)
        if anim_in == "slide_bottom" and in_dur > 0:
            target_y = self._position_y(position, H)
            y_expr = (
                f"if(lt(t,{in_dur:.3f}),"
                f"{H}-(({H}-({target_y}))*t/{in_dur:.3f}),"
                f"{target_y})"
            )
        elif anim_in == "slide_top" and in_dur > 0:
            target_y = self._position_y(position, H)
            y_expr = (
                f"if(lt(t,{in_dur:.3f}),"
                f"-text_h+(({H}/2)*t/{in_dur:.3f}),"
                f"{target_y})"
            )
        elif anim_in == "bounce" and in_dur > 0:
            target_y = self._position_y(position, H)
            y_expr = (
                f"if(lt(t,{in_dur:.3f}),"
                f"{target_y}+abs(sin(t/{in_dur:.3f}*PI))*({H}*0.3)*(1-t/{in_dur:.3f}),"
                f"{target_y})"
            )
        elif anim_in == "shake":
            x_expr = f"{self._position_x(position, W)}+3*sin(30*t)"
        elif anim_in == "pulse":
            # Pulse no afecta posición — se maneja vía zoom externo
            pass

        # X entrada (slides horizontales)
        if anim_in == "slide_left" and in_dur > 0:
            target_x = self._position_x(position, W)
            x_expr = (
                f"if(lt(t,{in_dur:.3f}),"
                f"-text_w+(({W}*0.5)*t/{in_dur:.3f}),"
                f"{target_x})"
            )
        elif anim_in == "slide_right" and in_dur > 0:
            target_x = self._position_x(position, W)
            x_expr = (
                f"if(lt(t,{in_dur:.3f}),"
                f"{W}-(({W}-({target_x}))*t/{in_dur:.3f}),"
                f"{target_x})"
            )

        # Salida slide
        if anim_out == "slide_out_bottom" and out_dur > 0 and out_start > 0:
            base_y = self._position_y(position, H)
            y_expr = (
                f"if(gt(t,{out_start:.3f}),"
                f"{base_y}+({H}*((t-{out_start:.3f})/{out_dur:.3f})),"
                f"{base_y})"
            )

        return x_expr, y_expr, alpha_expr

    def _build_animation_filter(self, anim_name: str, duration: float,
                                 phase: str) -> str:
        """
        Retorna expresión FFmpeg para la animación indicada.
        phase = 'in' | 'out' | 'loop'
        """
        anim = self.ANIMATIONS.get(anim_name, {})
        anim_dur = self._anim_duration(anim_name, duration)
        if phase == "in":
            if anim_name == "fade_in":
                return f"if(lt(t,{anim_dur:.3f}),t/{anim_dur:.3f},1)"
            if anim_name == "zoom_in":
                return f"if(lt(t,{anim_dur:.3f}),0.1+(0.9*t/{anim_dur:.3f}),1)"
        elif phase == "out":
            out_start = duration - anim_dur
            if anim_name == "fade_out":
                return f"if(gt(t,{out_start:.3f}),({duration:.3f}-t)/{anim_dur:.3f},1)"
        elif phase == "loop":
            if anim_name == "shake":
                return "3*sin(30*t)"
            if anim_name == "pulse":
                return "1+0.05*sin(2*PI*t)"
        return "1"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _position_x(position: str, W: int) -> str:
        mapping = {
            "center": "(w-text_w)/2",
            "top_center": "(w-text_w)/2",
            "bottom_center": "(w-text_w)/2",
            "top_left": "20",
            "bottom_left": "20",
            "top_right": f"w-text_w-20",
            "bottom_right": f"w-text_w-20",
            "middle_left": "20",
            "middle_right": f"w-text_w-20",
        }
        return mapping.get(position, "(w-text_w)/2")

    @staticmethod
    def _position_y(position: str, H: int) -> str:
        mapping = {
            "center": "(h-text_h)/2",
            "top_center": "30",
            "bottom_center": f"h-text_h-30",
            "top_left": "30",
            "bottom_left": f"h-text_h-30",
            "top_right": "30",
            "bottom_right": f"h-text_h-30",
            "middle_left": "(h-text_h)/2",
            "middle_right": "(h-text_h)/2",
        }
        return mapping.get(position, "(h-text_h)/2")

    def _anim_duration(self, anim_name: str, total_duration: float) -> float:
        anim = self.ANIMATIONS.get(anim_name, {})
        d = anim.get("duration", 0.0)
        if d == "auto":
            return min(total_duration * 0.3, 1.0)
        return float(d) if d else 0.0

    @staticmethod
    def _resolve_font(font_name: str) -> str:
        """Resuelve el nombre de fuente a un path de archivo TTF."""
        candidates = {
            "Arial": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "Arial Bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "Impact": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "Helvetica Neue": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "Montserrat Bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        }
        return candidates.get(font_name, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

    @staticmethod
    def _concat_clips(clip_paths: list[str], output_path: str) -> None:
        """Concatena clips de video en uno solo con ffmpeg concat filter."""
        if not clip_paths:
            return
        inputs: list[str] = []
        for p in clip_paths:
            inputs += ["-i", p]
        filter_complex = "".join(f"[{i}:v]" for i in range(len(clip_paths)))
        filter_complex += f"concat=n={len(clip_paths)}:v=1:a=0[v]"
        cmd = (
            ["ffmpeg", "-y"]
            + inputs
            + ["-filter_complex", filter_complex, "-map", "[v]",
               "-c:v", "qtrle", output_path]
        )
        subprocess.run(cmd, capture_output=True, timeout=300, check=True)
