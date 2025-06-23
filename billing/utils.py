from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from io import BytesIO
import os
from .models import Company, EmailLog

def generate_invoice_pdf(invoice):
    """
    Generate PDF for an invoice
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Get company info
    try:
        company = Company.objects.first()
    except Company.DoesNotExist:
        company = None
    
    # Get template settings
    template = invoice.template
    if not template:
        from .models import InvoiceTemplate
        template = InvoiceTemplate.objects.filter(is_default=True).first()
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor(template.header_color if template else '#3b82f6'),
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor(template.header_color if template else '#3b82f6')
    )
    
    normal_style = styles['Normal']
    right_align_style = ParagraphStyle(
        'RightAlign',
        parent=styles['Normal'],
        alignment=TA_RIGHT
    )
    
    # Add company logo if available and template allows
    if company and company.logo and template and template.show_logo:
        try:
            logo_path = os.path.join(settings.MEDIA_ROOT, company.logo.name)
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=2*inch, height=1*inch)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 12))
        except:
            pass
    
    # Title
    elements.append(Paragraph("FACTURE", title_style))
    elements.append(Spacer(1, 12))
    
    # Company and customer info table
    info_data = []
    
    # Company info
    company_info = []
    if company:
        company_info.append(f"<b>{company.name}</b>")
        if company.address:
            company_info.append(company.address.replace('\n', '<br/>'))
        if company.phone:
            company_info.append(f"Tél: {company.phone}")
        if company.email:
            company_info.append(f"Email: {company.email}")
        if company.tax_number:
            company_info.append(f"N° Fiscal: {company.tax_number}")
    
    # Customer info
    customer_info = []
    customer_info.append(f"<b>Facturé à:</b>")
    customer_info.append(f"<b>{invoice.customer.name}</b>")
    if invoice.customer.address:
        customer_info.append(invoice.customer.address.replace('\n', '<br/>'))
    if invoice.customer.phone:
        customer_info.append(f"Tél: {invoice.customer.phone}")
    if invoice.customer.email:
        customer_info.append(f"Email: {invoice.customer.email}")
    if invoice.customer.tax_number:
        customer_info.append(f"N° Fiscal: {invoice.customer.tax_number}")
    
    info_data.append([
        Paragraph('<br/>'.join(company_info), normal_style),
        Paragraph('<br/>'.join(customer_info), normal_style)
    ])
    
    info_table = Table(info_data, colWidths=[3*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Invoice details
    details_data = [
        ["Numéro de facture:", invoice.invoice_number],
        ["Date d'émission:", invoice.issue_date.strftime('%d/%m/%Y')],
        ["Date d'échéance:", invoice.due_date.strftime('%d/%m/%Y')],
    ]
    
    if invoice.reference:
        details_data.append(["Référence:", invoice.reference])
    
    details_table = Table(details_data, colWidths=[2*inch, 2*inch])
    details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(details_table)
    elements.append(Spacer(1, 20))
    
    # Invoice items table
    items_data = [['Description', 'Quantité', 'Prix unitaire', 'Total']]
    
    for item in invoice.items.all():
        items_data.append([
            item.description,
            f"{item.quantity:,.2f}",
            f"{item.unit_price:,.0f} GNF",
            f"{item.total:,.0f} GNF"
        ])
    
    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(template.header_color if template else '#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    elements.append(items_table)
    elements.append(Spacer(1, 20))
    
    # Totals table
    totals_data = []
    
    totals_data.append(['Sous-total:', f"{invoice.subtotal:,.0f} GNF"])
    
    if invoice.discount_amount > 0:
        totals_data.append([f'Remise ({invoice.discount_rate}%):', f"-{invoice.discount_amount:,.0f} GNF"])
    
    if invoice.tax_amount > 0:
        totals_data.append([f'TVA ({invoice.tax_rate}%):', f"{invoice.tax_amount:,.0f} GNF"])
    
    totals_data.append(['TOTAL:', f"{invoice.total_amount:,.0f} GNF"])
    
    totals_table = Table(totals_data, colWidths=[2*inch, 2*inch])
    totals_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, -2), (-1, -2), 1, colors.black),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f8f9fa')),
    ]))
    
    # Right align the totals table
    totals_table.hAlign = 'RIGHT'
    elements.append(totals_table)
    
    # Notes
    if invoice.notes:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Notes:", heading_style))
        elements.append(Paragraph(invoice.notes, normal_style))
    
    # Terms and conditions
    if template and template.terms_conditions:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Conditions générales:", heading_style))
        elements.append(Paragraph(template.terms_conditions, normal_style))
    
    # Footer
    if template and template.footer_text:
        elements.append(Spacer(1, 20))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        elements.append(Paragraph(template.footer_text, footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and return it
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf

def send_invoice_email(invoice, recipient, subject, message, send_copy=False, user=None):
    """
    Send invoice by email with PDF attachment
    """
    try:
        # Generate PDF
        pdf_content = generate_invoice_pdf(invoice)
        
        # Create email
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        
        # Add copy if requested
        if send_copy and user and user.email:
            email.cc = [user.email]
        
        # Attach PDF
        email.attach(
            f"facture_{invoice.invoice_number}.pdf",
            pdf_content,
            'application/pdf'
        )
        
        # Send email
        email.send()
        
        # Log successful email
        EmailLog.objects.create(
            invoice=invoice,
            recipient=recipient,
            subject=subject,
            sent_by=user,
            success=True
        )
        
        # Mark invoice as sent
        if invoice.status == 'draft':
            invoice.mark_as_sent()
        
        return True, "Email envoyé avec succès"
        
    except Exception as e:
        # Log failed email
        EmailLog.objects.create(
            invoice=invoice,
            recipient=recipient,
            subject=subject,
            sent_by=user,
            success=False,
            error_message=str(e)
        )
        
        return False, f"Erreur lors de l'envoi: {str(e)}"

def get_invoice_statistics(start_date=None, end_date=None):
    """
    Get invoice statistics for dashboard
    """
    from django.db.models import Sum, Count, Q
    from .models import Invoice
    
    queryset = Invoice.objects.all()
    
    if start_date:
        queryset = queryset.filter(issue_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(issue_date__lte=end_date)
    
    stats = {
        'total_invoices': queryset.count(),
        'total_amount': queryset.aggregate(total=Sum('total_amount'))['total'] or 0,
        'paid_invoices': queryset.filter(status='paid').count(),
        'paid_amount': queryset.filter(status='paid').aggregate(total=Sum('total_amount'))['total'] or 0,
        'pending_invoices': queryset.filter(status__in=['draft', 'sent']).count(),
        'pending_amount': queryset.filter(status__in=['draft', 'sent']).aggregate(total=Sum('total_amount'))['total'] or 0,
        'overdue_invoices': queryset.filter(status='overdue').count(),
        'overdue_amount': queryset.filter(status='overdue').aggregate(total=Sum('total_amount'))['total'] or 0,
    }
    
    return stats