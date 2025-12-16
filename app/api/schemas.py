"""
API Request/Response Schemas
Pydantic models for API validation
"""
from typing import Optional
from pydantic import BaseModel, Field


class RemoveBgRequest(BaseModel):
    """Request schema for /removebg endpoint"""
    image_file_b64: Optional[str] = Field(None, description="Base64 encoded image string")
    image_url: Optional[str] = Field(None, description="URL to download image from")
    size: Optional[str] = Field("preview", description="Output size: preview, full, or 50mp")
    type: Optional[str] = Field("auto", description="Background removal type")
    type_level: Optional[str] = Field("1", description="Quality level (1-3)")
    format: Optional[str] = Field("auto", description="Output format: auto, png, jpg")
    roi: Optional[str] = Field("0% 0% 100% 100%", description="Region of interest")
    crop: Optional[bool] = Field(False, description="Crop to foreground")
    crop_margin: Optional[str] = Field("0", description="Crop margin")
    scale: Optional[str] = Field("original", description="Scale output")
    position: Optional[str] = Field("original", description="Position")
    channels: Optional[str] = Field("rgba", description="Color channels: rgba, rgb")
    add_shadow: Optional[bool] = Field(False, description="Add shadow to result")
    shadow_type: Optional[str] = Field(None, description="Shadow type")
    shadow_opacity: Optional[str] = Field(None, description="Shadow opacity")
    semitransparency: Optional[bool] = Field(True, description="Semi-transparency")
    bg_color: Optional[str] = Field(None, description="Background color (hex)")
    bg_image_url: Optional[str] = Field(None, description="Background image URL")


class RemoveBgError(BaseModel):
    """Error response schema"""
    code: str
    title: str


class RemoveBgErrorResponse(BaseModel):
    """Error response wrapper"""
    errors: list[RemoveBgError]


class RemoveBgData(BaseModel):
    """Success response data"""
    result_b64: str = Field(..., description="Base64 encoded result image")
    foreground_top: int = Field(0, description="Top position of foreground")
    foreground_left: int = Field(0, description="Left position of foreground")
    foreground_width: int = Field(..., description="Width of foreground")
    foreground_height: int = Field(..., description="Height of foreground")


class RemoveBgResponse(BaseModel):
    """Success response wrapper"""
    data: RemoveBgData

