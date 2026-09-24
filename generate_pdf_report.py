import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to add 'Page X of Y' footers and running headers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running Header (Skip on Page 1)
        if self._pageNumber > 1:
            self.drawString(45, 755, "TECHNO WAREHOUSE PLANNING MODEL — SYSTEM LOGIC SPECIFICATION")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(45, 747, 612 - 45, 747)

            # Footer
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(612 - 45, 25, page_text)
            self.drawString(45, 25, "CONFIDENTIAL & PROPRIETARY — WMS & ALLOCATION LOGIC SPECIFICATION")
            self.line(45, 37, 612 - 45, 37)

        self.restoreState()


def create_pdf(filename="Techno_Warehouse_Planning_Model_Logic.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=42,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Define custom palette
    COLOR_PRIMARY = colors.HexColor("#1e1b4b")   # Dark Indigo / Navy
    COLOR_ACCENT = colors.HexColor("#4f46e5")    # Indigo
    COLOR_SECONDARY = colors.HexColor("#0284c7") # Ocean Blue
    COLOR_EMERALD = colors.HexColor("#059669")   # Emerald Green
    COLOR_DARK = colors.HexColor("#0f172a")      # Dark Slate
    COLOR_BORDER = colors.HexColor("#cbd5e1")    # Border Grey

    # Custom typography styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=COLOR_PRIMARY,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=COLOR_ACCENT,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=COLOR_PRIMARY,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=COLOR_ACCENT,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=COLOR_DARK,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        'Callout_Text',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=COLOR_DARK
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1 # Center
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=COLOR_DARK
    )

    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=table_cell_style,
        alignment=1
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell_style,
        fontName='Helvetica-Bold'
    )

    story = []

    # -------------------------------------------------------------------------
    # COVER / HEADER BLOCK
    # -------------------------------------------------------------------------
    story.append(Paragraph("TECHNO WAREHOUSE PLANNING MODEL", title_style))
    story.append(Paragraph("COMPLETE SYSTEM ARCHITECTURE, BUSINESS LOGIC & ALLOCATION ENGINES", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_ACCENT, spaceAfter=10))

    # Executive Overview Callout Box
    overview_html = """<b>EXECUTIVE SUMMARY:</b> The Techno Warehouse Planning & Allocation Model is an enterprise supply chain intelligence engine designed to optimize multi-warehouse inventory distribution, automate sales-driven ABC categorization, execute size & style-constrained inventory allocation from central mother hubs, and validate multi-stage projected stock availability across regional fulfillment centers."""
    
    overview_table = Table([[Paragraph(overview_html, callout_style)]], colWidths=[522])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 1, COLOR_ACCENT),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 10))

    # Document Details Grid
    doc_info_data = [
        [Paragraph("<b>System Core:</b> Python Flask / Pandas Engine", body_style), Paragraph("<b>Primary Mother Hub:</b> Bagalur Hub", body_style)],
        [Paragraph("<b>Regional Hubs:</b> Bhiwandi, Gurugram, Kolkata", body_style), Paragraph("<b>Allocation Engines:</b> Dynamic Capping & Box-Wise Models", body_style)],
        [Paragraph("<b>Data Ingestion:</b> Sales & WMS CSV/Excel Files", body_style), Paragraph("<b>Validation Pipeline:</b> Raw, In-Transit, & Projected Stock", body_style)],
    ]
    doc_info_table = Table(doc_info_data, colWidths=[261, 261])
    doc_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(doc_info_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # SECTION 1: SYSTEM OVERVIEW & WAREHOUSE ARCHITECTURE
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. System Overview & Warehouse Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=6))
    
    story.append(Paragraph(
        "The system coordinates inventory across <b>four strategic fulfillment locations</b> in India. "
        "Central inventory originates at the primary manufacturing/distribution center in Bagalur and is algorithmically pushed to regional fulfillment nodes:",
        body_style
    ))

    wh_arch_data = [
        [Paragraph("Warehouse ID", table_header_style), Paragraph("Location Name", table_header_style), Paragraph("Role & Priority", table_header_style), Paragraph("Default Split Strategy", table_header_style)],
        [Paragraph("<b>wms_bagalur</b>", table_cell_bold), Paragraph("Bagalur Hub", table_cell_style), Paragraph("Primary Mother Warehouse / Retention Center", table_cell_style), Paragraph("Retains 64% base stock + excess uncapped stock", table_cell_style)],
        [Paragraph("<b>wms_bhiwandi</b>", table_cell_bold), Paragraph("Bhiwandi (West)", table_cell_style), Paragraph("Priority 1 Push Warehouse (P1)", table_cell_style), Paragraph("Receives 17% base push allocation", table_cell_style)],
        [Paragraph("<b>wms_kolkata</b>", table_cell_bold), Paragraph("Kolkata (East)", table_cell_style), Paragraph("Priority 2 Push Warehouse (P2)", table_cell_style), Paragraph("Receives 14% base push allocation", table_cell_style)],
        [Paragraph("<b>wms_ggn</b>", table_cell_bold), Paragraph("Gurugram (North)", table_cell_style), Paragraph("Priority 3 Push Warehouse (P3)", table_cell_style), Paragraph("Receives 5% (or residual push) allocation", table_cell_style)],
    ]
    wh_arch_table = Table(wh_arch_data, colWidths=[80, 100, 170, 172])
    wh_arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(wh_arch_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # SECTION 2: SALES-DRIVEN ABC INVENTORY CLASSIFICATION
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Sales-Driven ABC Inventory Classification Logic", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=6))
    
    story.append(Paragraph(
        "To ensure high-performing SKUs receive maximum warehouse presence while long-tail inventory remains centralized, the system performs dynamic Pareto ABC analysis based on aggregate historical sales volume.",
        body_style
    ))

    story.append(Paragraph("<b>Mathematical Formula & Cumulative Sales Ranking:</b>", h2_style))
    story.append(Paragraph("1. Aggregates sales by SKU: <i>Total Sales Qty = &Sigma; (Sales Qty per SKU)</i>.", bullet_style))
    story.append(Paragraph("2. Sorts SKUs descending by sales quantity.", bullet_style))
    story.append(Paragraph("3. Calculates Cumulative Sales Percentage: <i>Cumulative % = (&Sigma; Cumulative Qty / Total System Sales) &times; 100</i>.", bullet_style))
    story.append(Paragraph("4. Assigns Category Code based on exact cutoffs:", bullet_style))

    abc_tier_data = [
        [Paragraph("Category", table_header_style), Paragraph("Cumulative Sales Cutoff", table_header_style), Paragraph("SKU Strategic Focus", table_header_style), Paragraph("Target Warehouse Coverage", table_header_style)],
        [Paragraph("<b>Category A</b>", table_cell_bold), Paragraph("0.00% – 50.00%", table_cell_center), Paragraph("Top-selling velocity SKUs generating 50% of revenue.", table_cell_style), Paragraph("Target <b>4 / 4 Warehouses</b> (Full Regional Coverage)", table_cell_style)],
        [Paragraph("<b>Category B</b>", table_cell_bold), Paragraph("50.01% – 75.00%", table_cell_center), Paragraph("Medium-velocity core styles generating next 25% sales.", table_cell_style), Paragraph("Target <b>2 to 3 Warehouses</b>", table_cell_style)],
        [Paragraph("<b>Category C</b>", table_cell_bold), Paragraph("75.01% – 100.00%", table_cell_center), Paragraph("Slow-moving / long-tail SKUs generating bottom 25%.", table_cell_style), Paragraph("Centralized in <b>1 Mother Warehouse (Bagalur)</b>", table_cell_style)],
    ]
    abc_tier_table = Table(abc_tier_data, colWidths=[70, 120, 182, 150])
    abc_tier_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_ACCENT),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(abc_tier_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # SECTION 3: WAREHOUSE COVERAGE & PIVOTING ANALYTICS
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. Warehouse Stock Pivoting & Coverage Metrics", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=6))
    
    story.append(Paragraph(
        "The analytics core dynamically pivots physical WMS inventory records across fulfillment locations. "
        "For each SKU, the system computes the <b>Warehouse Coverage Count (0 to 4 WHs)</b>:",
        body_style
    ))
    story.append(Paragraph("<b>Formula:</b> <i>WH Count = Count of Warehouses where Total Available Quantity > 0</i>", bullet_style))
    story.append(Paragraph("<b>Category Health Index:</b> Calculates average warehouse presence per category: <i>Avg WH Coverage = &sum;(WH Count per SKU) / Total SKUs in Category</i>.", bullet_style))
    story.append(Paragraph("<b>Zero-Stock Gap Analysis:</b> Identifies Category A SKUs with <i>Total Stock = 0</i> across all warehouses as critical out-of-stock risk alerts.", bullet_style))

    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # SECTION 4: ALLOCATION ENGINE 1 — DYNAMIC SIZE & STYLE CAPPING
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. Allocation Engine 1: Dynamic Size & Style Capping", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=6))
    
    story.append(Paragraph(
        "The Dynamic Allocation Planner processes available stock at Bagalur and determines optimal quantities to dispatch to Bhiwandi, Kolkata, and Gurugram using a <b>4-stage constraint hierarchy</b>:",
        body_style
    ))

    stage1 = "<b>Stage 1: Base Ratio Split:</b> 64% retained at Bagalur. 36% Push Pool split as Bhiwandi=17%, Kolkata=14%, Gurugram=5%."
    stage2 = "<b>Stage 2: Size-Specific Maximum Capping:</b> Pushed quantities per WH are capped against gender/size MAX limits. Excess is redirected to Bagalur."
    stage3 = "<b>Stage 3: Size-Specific Minimum Capping:</b> If allocated qty < MIN cap (e.g. MIN=5), push is canceled (set to 0) and retained at Bagalur."
    stage4 = "<b>Stage 4: Aggregate Style-Level NS & PS Capping:</b> Sizes grouped into Normal (NS: S–2XL) and Plus (PS: 3XL–5XL). If aggregate style-color push to a WH is < overall MIN cap (e.g. Mens NS Min = 25 pcs), ALL size allocations for that style to that WH revert to Bagalur."

    story.append(Paragraph(stage1, bullet_style))
    story.append(Paragraph(stage2, bullet_style))
    story.append(Paragraph(stage3, bullet_style))
    story.append(Paragraph(stage4, bullet_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Size-Level Capping Reference Table (Mens vs Womens):</b>", h2_style))

    caps_table_data = [
        [Paragraph("Category / Size", table_header_style), Paragraph("Kolkata Caps (MIN / MAX)", table_header_style), Paragraph("Bhiwandi Caps (MIN / MAX)", table_header_style), Paragraph("Gurugram Caps (MIN / MAX)", table_header_style)],
        [Paragraph("<b>Mens S / M</b>", table_cell_bold), Paragraph("Min: 5 | Max: 15–20", table_cell_center), Paragraph("Min: 5 | Max: 15–20", table_cell_center), Paragraph("Min: 5 | Max: 10–15", table_cell_center)],
        [Paragraph("<b>Mens L / XL</b>", table_cell_bold), Paragraph("Min: 5 | Max: 30", table_cell_center), Paragraph("Min: 5 | Max: 30", table_cell_center), Paragraph("Min: 5 | Max: 20", table_cell_center)],
        [Paragraph("<b>Mens 2XL</b>", table_cell_bold), Paragraph("Min: 5 | Max: 20", table_cell_center), Paragraph("Min: 5 | Max: 20", table_cell_center), Paragraph("Min: 5 | Max: 10", table_cell_center)],
        [Paragraph("<b>Mens 3XL (PS)</b>", table_cell_bold), Paragraph("Min: 3 | Max: 10", table_cell_center), Paragraph("Min: 3 | Max: 10", table_cell_center), Paragraph("Min: 0 | Max: 0 (No Push)", table_cell_center)],
        [Paragraph("<b>Mens 4XL / 5XL (PS)</b>", table_cell_bold), Paragraph("Min: 2 | Max: 5", table_cell_center), Paragraph("Min: 2 | Max: 5", table_cell_center), Paragraph("Min: 0 | Max: 0 (No Push)", table_cell_center)],
        [Paragraph("<b>Womens S to 2XL</b>", table_cell_bold), Paragraph("Min: 3 | Max: 10–20", table_cell_center), Paragraph("Min: 3 | Max: 10–20", table_cell_center), Paragraph("Min: 3 | Max: 5–15", table_cell_center)],
        [Paragraph("<b>Womens 3XL to 5XL</b>", table_cell_bold), Paragraph("Min: 0 | Max: 0 (No Push)", table_cell_center), Paragraph("Min: 0 | Max: 0 (No Push)", table_cell_center), Paragraph("Min: 0 | Max: 0 (No Push)", table_cell_center)],
    ]
    caps_table = Table(caps_table_data, colWidths=[114, 136, 136, 136])
    caps_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(caps_table)

    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Overall Style-Level NS & PS Minimum Thresholds:</b>", h2_style))
    
    style_caps_data = [
        [Paragraph("Group Type", table_header_style), Paragraph("Size Range Included", table_header_style), Paragraph("Kolkata Min Threshold", table_header_style), Paragraph("Bhiwandi Min Threshold", table_header_style), Paragraph("Gurugram Min Threshold", table_header_style)],
        [Paragraph("<b>Mens NS Group</b>", table_cell_bold), Paragraph("S, M, L, XL, 2XL", table_cell_style), Paragraph("<b>25 Pieces</b>", table_cell_center), Paragraph("<b>25 Pieces</b>", table_cell_center), Paragraph("<b>25 Pieces</b>", table_cell_center)],
        [Paragraph("<b>Mens PS Group</b>", table_cell_bold), Paragraph("3XL, 4XL, 5XL", table_cell_style), Paragraph("<b>7 Pieces</b>", table_cell_center), Paragraph("<b>7 Pieces</b>", table_cell_center), Paragraph("<b>0 Pieces</b>", table_cell_center)],
        [Paragraph("<b>Womens NS Group</b>", table_cell_bold), Paragraph("S, M, L, XL, 2XL", table_cell_style), Paragraph("<b>3 Pieces</b>", table_cell_center), Paragraph("<b>3 Pieces</b>", table_cell_center), Paragraph("<b>3 Pieces</b>", table_cell_center)],
    ]
    style_caps_table = Table(style_caps_data, colWidths=[100, 118, 101, 101, 102])
    style_caps_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(style_caps_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # SECTION 5: ALLOCATION ENGINE 2 — BOX-WISE ALLOCATION MODEL
    # -------------------------------------------------------------------------
    story.append(Paragraph("5. Allocation Engine 2: Box-Wise Allocation Model", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=6))
    
    story.append(Paragraph(
        "For standardized carton-based fulfillment, the portal provides a specialized <b>Box-Wise Allocation Engine</b>. "
        "It converts unit allocations into exact master box counts (Standard = 10 pcs/box):",
        body_style
    ))

    story.append(Paragraph("1. <b>Total Master Boxes:</b> <i>Total Boxes = Grand Total Qty / Per Box Qty (rounded to 2 decimals)</i>", bullet_style))
    story.append(Paragraph("2. <b>Kolkata Alloc Qty:</b> <i>Kolkata Alloc = MIN(Size Rule Cap, Grand Total &times; 10%)</i>", bullet_style))
    story.append(Paragraph("3. <b>Bhiwandi Alloc Qty:</b> <i>Bhiwandi Alloc = MIN(Size Rule Cap, Grand Total &times; 10%)</i>", bullet_style))
    story.append(Paragraph("4. <b>Gurugram Alloc Qty:</b> <i>Gurugram Alloc = MIN(Size Rule Cap, Grand Total &times; 6%)</i>", bullet_style))
    story.append(Paragraph("5. <b>Bagalur Retained Stock:</b> <i>Bagalur Retained = Grand Total - (Kolkata + Bhiwandi + Gurugram Pushed Qty)</i>", bullet_style))

    story.append(Spacer(1, 6))

    box_rules_data = [
        [Paragraph("Size Code", table_header_style), Paragraph("Rule Mapping", table_header_style), Paragraph("Kolkata Max Rule", table_header_style), Paragraph("Bhiwandi Max Rule", table_header_style), Paragraph("Gurugram Max Rule", table_header_style)],
        [Paragraph("<b>S</b>", table_cell_bold), Paragraph("SML Rule", table_cell_center), Paragraph("15 pcs", table_cell_center), Paragraph("15 pcs", table_cell_center), Paragraph("10 pcs", table_cell_center)],
        [Paragraph("<b>M</b>", table_cell_bold), Paragraph("MED Rule", table_cell_center), Paragraph("20 pcs", table_cell_center), Paragraph("20 pcs", table_cell_center), Paragraph("15 pcs", table_cell_center)],
        [Paragraph("<b>L / XL</b>", table_cell_bold), Paragraph("LAR / XLR Rule", table_cell_center), Paragraph("30 pcs", table_cell_center), Paragraph("30 pcs", table_cell_center), Paragraph("25 pcs", table_cell_center)],
        [Paragraph("<b>2XL</b>", table_cell_bold), Paragraph("2XL Rule", table_cell_center), Paragraph("20 pcs", table_cell_center), Paragraph("20 pcs", table_cell_center), Paragraph("15 pcs", table_cell_center)],
        [Paragraph("<b>3XL / 4XL / 5XL</b>", table_cell_bold), Paragraph("Plus Size Rules", table_cell_center), Paragraph("5 pcs", table_cell_center), Paragraph("5 pcs", table_cell_center), Paragraph("2 pcs", table_cell_center)],
        [Paragraph("<b>06Y – 10Y (Kids)</b>", table_cell_bold), Paragraph("Junior Size Rules", table_cell_center), Paragraph("8 pcs", table_cell_center), Paragraph("6 pcs", table_cell_center), Paragraph("6 pcs", table_cell_center)],
        [Paragraph("<b>12Y – 16Y (Kids)</b>", table_cell_bold), Paragraph("Senior Kids Rules", table_cell_center), Paragraph("10 pcs", table_cell_center), Paragraph("8 pcs", table_cell_center), Paragraph("6 pcs", table_cell_center)],
    ]
    box_rules_table = Table(box_rules_data, colWidths=[90, 110, 107, 107, 108])
    box_rules_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_EMERALD),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(box_rules_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # SECTION 6: WAREHOUSE VALIDATION & PIPELINE PROJECTION
    # -------------------------------------------------------------------------
    story.append(Paragraph("6. Warehouse Validation & 3-Stage Pipeline Projection", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=6))
    
    story.append(Paragraph(
        "The Warehouse Validation tab reconciles physical warehouse stock against planned allocation transfers and incoming factory shipments across <b>three comparative pipeline stages</b>:",
        body_style
    ))

    validation_comp_data = [
        [Paragraph("Pipeline View Stage", table_header_style), Paragraph("Stock Included in Calculation", table_header_style), Paragraph("SKU Coverage Impact Target", table_header_style)],
        [Paragraph("<b>Raw Stock Only</b>", table_cell_bold), Paragraph("Physical stock in warehouse WMS", table_cell_style), Paragraph("Establishes baseline regional stock gaps.", table_cell_style)],
        [Paragraph("<b>Raw + In-Transit</b>", table_cell_bold), Paragraph("Physical Stock + Incoming Supply Shipments", table_cell_style), Paragraph("Highlights incoming relief before allocation.", table_cell_style)],
        [Paragraph("<b>Fully Projected</b>", table_cell_bold), Paragraph("Allocated Pushed Stock + In-Transit Shipments", table_cell_style), Paragraph("Validates shift of Category A SKUs towards <b>4 / 4 WH Coverage</b>.", table_cell_style)],
    ]
    val_comp_table = Table(validation_comp_data, colWidths=[120, 190, 212])
    val_comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(val_comp_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # SECTION 7: REST API MATRIX & DATA SCHEMAS
    # -------------------------------------------------------------------------
    story.append(Paragraph("7. REST API Endpoints & Technical Data Matrix", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=6))
    
    api_data = [
        [Paragraph("Endpoint Route", table_header_style), Paragraph("Method", table_header_style), Paragraph("Function & Payload Output", table_header_style)],
        [Paragraph("<b>/api/summary</b>", table_cell_bold), Paragraph("GET", table_cell_center), Paragraph("Returns system total SKUs, total sales, ABC breakdown, stock per warehouse, and overall WH distribution.", table_cell_style)],
        [Paragraph("<b>/api/details</b>", table_cell_bold), Paragraph("GET", table_cell_center), Paragraph("Returns paginated SKU records with sales rank, sales qty, category, size/color metadata, and per-WH quantities. Supports search & WH filter.", table_cell_style)],
        [Paragraph("<b>/api/run_allocation</b>", table_cell_bold), Paragraph("GET", table_cell_center), Paragraph("Executes Dynamic Capping Planner across inventory dataset; outputs summary statistics and exports allocation_output.csv.", table_cell_style)],
        [Paragraph("<b>/api/run_boxwise_allocation</b>", table_cell_bold), Paragraph("GET", table_cell_center), Paragraph("Executes Box-Wise Allocation Engine; calculates allocated units, box counts per WH, and exports allocation_output.csv.", table_cell_style)],
        [Paragraph("<b>/api/validation</b>", table_cell_bold), Paragraph("GET", table_cell_center), Paragraph("Returns 3-stage validation records comparing Current, In-Transit, and Projected stock across all 4 warehouses.", table_cell_style)],
        [Paragraph("<b>/api/download_allocation</b>", table_cell_bold), Paragraph("GET", table_cell_center), Paragraph("Downloads the generated allocation output CSV file for execution by warehouse operations.", table_cell_style)],
    ]
    api_table = Table(api_data, colWidths=[130, 50, 342])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_ACCENT),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(api_table)
    story.append(Spacer(1, 10))

    # Sign-off footer block
    signoff_html = "<b>DOCUMENT CONTROL & SYSTEM AUTHORIZATION:</b> This document specifies the complete algorithmic logic for the Techno Warehouse Planning Model. Approved for operational deployment and system audit."
    signoff_table = Table([[Paragraph(signoff_html, callout_style)]], colWidths=[522])
    signoff_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 1, COLOR_PRIMARY),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(signoff_table)

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated: {filename}")

if __name__ == "__main__":
    create_pdf()
