"""
Generador de facturas en PDF
Utiliza ReportLab para crear PDFs profesionales
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import os
from datetime import datetime
import qrcode
from io import BytesIO

class InvoiceGenerator:
    """Generador de facturas en PDF"""
    
    @staticmethod
    def generate_pdf(invoice, order, output_path):
        """
        Generar PDF de factura
        
        Args:
            invoice: Objeto Invoice
            order: Objeto Order
            output_path: Ruta donde guardar el PDF
        """
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Crear documento
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Contenedor de elementos
        elements = []
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12
        )
        
        # 1. Encabezado con logo y título
        elements.append(Paragraph('FACTURA ELECTRÓNICA', title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # 2. Información del emisor y receptor
        emisor_receptor_data = [
            ['EMISOR', 'RECEPTOR'],
            [invoice.razon_social_emisor, invoice.razon_social_receptor],
            [f'RFC: {invoice.rfc_emisor}', f'RFC: {invoice.rfc_receptor}'],
            ['', f'Dirección: {invoice.direccion_fiscal or "N/A"}'],
            ['', f'CP: {invoice.codigo_postal or "N/A"}'],
            ['', f'Régimen Fiscal: {invoice.regimen_fiscal or "N/A"}']
        ]
        
        emisor_receptor_table = Table(emisor_receptor_data, colWidths=[3.5*inch, 3.5*inch])
        emisor_receptor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        
        elements.append(emisor_receptor_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # 3. Datos de la factura
        factura_data = [
            ['Folio:', invoice.folio, 'UUID:', invoice.uuid[:18] + '...'],
            ['Fecha Emisión:', invoice.fecha_emision.strftime('%d/%m/%Y %H:%M'), 'Método Pago:', 'PUE - Pago en una exhibición'],
            ['Fecha Timbrado:', invoice.fecha_timbrado.strftime('%d/%m/%Y %H:%M'), 'Forma Pago:', InvoiceGenerator._get_forma_pago(invoice.forma_pago)],
            ['Uso CFDI:', InvoiceGenerator._get_uso_cfdi(invoice.uso_cfdi), 'Moneda:', 'MXN - Peso Mexicano']
        ]
        
        factura_table = Table(factura_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
        factura_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(factura_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # 4. Conceptos (productos)
        elements.append(Paragraph('CONCEPTOS', heading_style))
        
        conceptos_data = [['Cantidad', 'Descripción', 'Precio Unitario', 'Importe']]
        
        for item in order.items:
            conceptos_data.append([
                str(item.quantity),
                item.product_name,
                f'${item.price:,.2f}',
                f'${item.get_subtotal():,.2f}'
            ])
        
        conceptos_table = Table(conceptos_data, colWidths=[1*inch, 3.5*inch, 1.5*inch, 1.5*inch])
        conceptos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ]))
        
        elements.append(conceptos_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # 5. Totales
        totales_data = [
            ['Subtotal:', f'${invoice.subtotal:,.2f}'],
            ['IVA (16%):', f'${invoice.iva:,.2f}'],
            ['TOTAL:', f'${invoice.total:,.2f}']
        ]
        
        totales_table = Table(totales_data, colWidths=[5.5*inch, 1.5*inch])
        totales_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 1), 10),
            ('FONTSIZE', (0, 2), (-1, 2), 14),
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor('#e74c3c')),
            ('LINEABOVE', (0, 2), (-1, 2), 2, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(totales_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # 6. QR Code y sello digital
        qr_img = InvoiceGenerator._generate_qr(invoice)
        if qr_img:
            elements.append(Paragraph('CÓDIGO QR DE VERIFICACIÓN', heading_style))
            elements.append(qr_img)
            elements.append(Spacer(1, 0.2*inch))
        
        # 7. Sello digital (simplificado)
        if invoice.sello_digital:
            sello_style = ParagraphStyle(
                'Sello',
                parent=styles['Normal'],
                fontSize=7,
                textColor=colors.grey
            )
            elements.append(Paragraph('<b>Sello Digital del CFDI:</b>', styles['Normal']))
            elements.append(Paragraph(invoice.sello_digital[:200] + '...', sello_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # 8. Nota legal
        nota_style = ParagraphStyle(
            'Nota',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        elements.append(Paragraph(
            'Este documento es una representación impresa de un CFDI<br/>'
            'Para verificar su validez consulte: www.sat.gob.mx',
            nota_style
        ))
        
        # Construir PDF
        doc.build(elements)
        
        return output_path
    
    @staticmethod
    def _generate_qr(invoice):
        """Generar código QR con información de la factura"""
        try:
            # Datos para el QR (formato simplificado)
            qr_data = f"https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?id={invoice.uuid}&re={invoice.rfc_emisor}&rr={invoice.rfc_receptor}&tt={invoice.total:.6f}"
            
            # Generar QR
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Guardar en BytesIO
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Crear imagen de ReportLab
            return Image(buffer, width=1.5*inch, height=1.5*inch)
        except ValueError:
            return None
    
    @staticmethod
    def _get_forma_pago(codigo):
        """Obtener descripción de forma de pago"""
        formas = {
            '01': 'Efectivo',
            '02': 'Cheque nominativo',
            '03': 'Transferencia electrónica',
            '04': 'Tarjeta de crédito',
            '28': 'Tarjeta de débito',
            '99': 'Por definir'
        }
        return f'{codigo} - {formas.get(codigo, "Otro")}'
    
    @staticmethod
    def _get_uso_cfdi(codigo):
        """Obtener descripción de uso de CFDI"""
        usos = {
            'G01': 'Adquisición de mercancías',
            'G02': 'Devoluciones, descuentos o bonificaciones',
            'G03': 'Gastos en general',
            'I01': 'Construcciones',
            'I02': 'Mobiliario y equipo de oficina',
            'I03': 'Equipo de transporte',
            'I04': 'Equipo de cómputo',
            'P01': 'Por definir'
        }
        return f'{codigo} - {usos.get(codigo, "Otro")}'
