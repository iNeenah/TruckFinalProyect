import logging
from typing import Dict, Any
from app.models.route import CalculatedRoute
from app.schemas.route import RouteResponse

logger = logging.getLogger(__name__)

def generate_route_report(route: CalculatedRoute) -> bytes:
    """
    Generate a PDF report for a calculated route.
    
    Args:
        route: The calculated route to generate report for
        
    Returns:
        bytes: PDF content as bytes
    """
    try:
        # Import PDF generation library
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        # Create PDF in memory
        from io import BytesIO
        buffer = BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
        )
        title = Paragraph("Reporte de Ruta Optimizada", title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Route information
        info_data = [
            ['Origen:', route.origin],
            ['Destino:', route.destination],
            ['Distancia:', f"{route.distance / 1000:.2f} km"],
            ['Duración:', f"{route.duration // 60}h {route.duration % 60}m"],
            ['Costo Total:', f"${route.total_cost:,.2f}"],
            ['Costo Combustible:', f"${route.fuel_cost:,.2f}"],
            ['Costo Peajes:', f"${route.toll_cost:,.2f}"],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, 0), colors.beige),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 24))
        
        # Cost analysis
        cost_data = [
            ['Concepto', 'Monto'],
            ['Combustible', f"${route.fuel_cost:,.2f}"],
            ['Peajes', f"${route.toll_cost:,.2f}"],
            ['Total', f"${route.total_cost:,.2f}"],
        ]
        
        cost_table = Table(cost_data, colWidths=[4*inch, 2*inch])
        cost_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("Análisis de Costos", styles['Heading2']))
        story.append(Spacer(1, 12))
        story.append(cost_table)
        story.append(Spacer(1, 24))
        
        # Footer
        story.append(Paragraph("Reporte generado automáticamente por Kiro Optimizador de Rutas", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        logger.info(f"PDF report generated successfully for route {route.id}")
        return pdf_content
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        raise

def generate_statistics_report(stats: Dict[str, Any]) -> bytes:
    """
    Generate a PDF report for route statistics.
    
    Args:
        stats: Statistics data to include in report
        
    Returns:
        bytes: PDF content as bytes
    """
    try:
        # Import PDF generation library
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        # Create PDF in memory
        from io import BytesIO
        buffer = BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
        )
        title = Paragraph("Reporte de Estadísticas", title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Statistics information
        stats_data = [
            ['Métrica', 'Valor'],
            ['Rutas Totales', str(stats.get('total_routes', 0))],
            ['Distancia Total', f"{stats.get('total_distance_km', 0):,.2f} km"],
            ['Ahorro Total', f"${stats.get('total_savings', 0):,.2f}"],
            ['Ahorro Promedio', f"${stats.get('average_savings', 0):,.2f}"],
        ]
        
        stats_table = Table(stats_data, colWidths=[4*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 24))
        
        # Footer
        story.append(Paragraph("Reporte generado automáticamente por Kiro Optimizador de Rutas", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        logger.info("Statistics PDF report generated successfully")
        return pdf_content
        
    except Exception as e:
        logger.error(f"Error generating statistics PDF report: {e}")
        raise