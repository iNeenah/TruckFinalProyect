import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { RouteFeature, Location, TollPoint } from '../types/map';
import { Vehicle } from '../types/vehicle';
import { formatDistance, formatDuration } from '../types/map';
import { formatRouteCost } from '../hooks/useRoutes';

export interface RouteReportData {
  routes: RouteFeature[];
  selectedRoute: RouteFeature;
  origin: Location;
  destination: Location;
  waypoints?: Location[];
  vehicle: Vehicle;
  tollPoints?: TollPoint[];
  calculatedAt: Date;
  companyInfo?: {
    name: string;
    logo?: string;
    address?: string;
    phone?: string;
    email?: string;
  };
}

export interface ReportOptions {
  format: 'complete' | 'simple' | 'comparison';
  includeMap: boolean;
  includeRouteDetails: boolean;
  includeCostBreakdown: boolean;
  includeTollDetails: boolean;
  includeVehicleInfo: boolean;
  language: 'es' | 'en';
}

class ReportService {
  private readonly pageWidth = 210; // A4 width in mm
  private readonly pageHeight = 297; // A4 height in mm
  private readonly margin = 20;

  /**
   * Generate PDF report for route calculation
   */
  async generateRouteReport(
    data: RouteReportData,
    options: ReportOptions = this.getDefaultOptions()
  ): Promise<void> {
    const pdf = new jsPDF('p', 'mm', 'a4');
    
    try {
      // Add header
      await this.addHeader(pdf, data, options);
      
      // Add route summary
      this.addRouteSummary(pdf, data, options);
      
      // Add map if requested
      if (options.includeMap) {
        await this.addMapImage(pdf, data);
      }
      
      // Add route details based on format
      switch (options.format) {
        case 'complete':
          await this.addCompleteRouteDetails(pdf, data, options);
          break;
        case 'simple':
          await this.addSimpleRouteDetails(pdf, data, options);
          break;
        case 'comparison':
          await this.addRouteComparison(pdf, data, options);
          break;
      }
      
      // Add footer
      this.addFooter(pdf, data, options);
      
      // Save the PDF
      const fileName = this.generateFileName(data, options);
      pdf.save(fileName);
      
    } catch (error) {
      console.error('Error generating PDF report:', error);
      throw new Error('Failed to generate PDF report');
    }
  }

  /**
   * Generate mobile-optimized route sheet
   */
  async generateMobileRouteSheet(
    data: RouteReportData,
    options: Partial<ReportOptions> = {}
  ): Promise<void> {
    const mobileOptions: ReportOptions = {
      ...this.getDefaultOptions(),
      format: 'simple',
      includeMap: false,
      includeRouteDetails: true,
      includeCostBreakdown: true,
      includeTollDetails: false,
      includeVehicleInfo: false,
      ...options,
    };

    // Use smaller page size for mobile
    const pdf = new jsPDF('p', 'mm', [148, 210]); // A5 size
    
    try {
      // Mobile-specific header
      await this.addMobileHeader(pdf, data, mobileOptions);
      
      // Compact route info
      this.addCompactRouteInfo(pdf, data, mobileOptions);
      
      // Essential details only
      this.addEssentialDetails(pdf, data, mobileOptions);
      
      // Save with mobile-specific filename
      const fileName = this.generateFileName(data, mobileOptions, 'mobile');
      pdf.save(fileName);
      
    } catch (error) {
      console.error('Error generating mobile route sheet:', error);
      throw new Error('Failed to generate mobile route sheet');
    }
  }

  /**
   * Capture map screenshot for PDF inclusion
   */
  private async captureMapScreenshot(): Promise<string | null> {
    try {
      const mapContainer = document.querySelector('.mapboxgl-map') as HTMLElement;
      if (!mapContainer) {
        console.warn('Map container not found for screenshot');
        return null;
      }

      const canvas = await html2canvas(mapContainer, {
        useCORS: true,
        allowTaint: true,
        scale: 1,
        width: mapContainer.offsetWidth,
        height: mapContainer.offsetHeight,
      });

      return canvas.toDataURL('image/png');
    } catch (error) {
      console.error('Error capturing map screenshot:', error);
      return null;
    }
  }

  /**
   * Add header to PDF
   */
  private async addHeader(
    pdf: jsPDF,
    data: RouteReportData,
    options: ReportOptions
  ): Promise<void> {
    let yPosition = this.margin;

    // Company logo and info
    if (data.companyInfo) {
      if (data.companyInfo.logo) {
        try {
          pdf.addImage(data.companyInfo.logo, 'PNG', this.margin, yPosition, 30, 15);
        } catch (error) {
          console.warn('Could not add company logo:', error);
        }
      }
      
      pdf.setFontSize(16);
      pdf.setFont('helvetica', 'bold');
      pdf.text(data.companyInfo.name, this.margin + 35, yPosition + 8);
      
      yPosition += 20;
    }

    // Report title
    pdf.setFontSize(20);
    pdf.setFont('helvetica', 'bold');
    const title = options.language === 'es' ? 'Reporte de Ruta' : 'Route Report';
    pdf.text(title, this.margin, yPosition);
    
    yPosition += 10;

    // Report date and time
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    const dateLabel = options.language === 'es' ? 'Generado el:' : 'Generated on:';
    pdf.text(
      `${dateLabel} ${data.calculatedAt.toLocaleString(options.language === 'es' ? 'es-AR' : 'en-US')}`,
      this.margin,
      yPosition
    );

    // Add line separator
    yPosition += 10;
    pdf.line(this.margin, yPosition, this.pageWidth - this.margin, yPosition);
  }

  /**
   * Add route summary section
   */
  private addRouteSummary(
    pdf: jsPDF,
    data: RouteReportData,
    options: ReportOptions
  ): void {
    let yPosition = 60;

    pdf.setFontSize(14);
    pdf.setFont('helvetica', 'bold');
    const summaryTitle = options.language === 'es' ? 'Resumen de Ruta' : 'Route Summary';
    pdf.text(summaryTitle, this.margin, yPosition);
    
    yPosition += 10;

    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');

    // Origin and destination
    const fromLabel = options.language === 'es' ? 'Desde:' : 'From:';
    const toLabel = options.language === 'es' ? 'Hasta:' : 'To:';
    
    pdf.text(`${fromLabel} ${data.origin.name}`, this.margin, yPosition);
    yPosition += 5;
    pdf.text(`${toLabel} ${data.destination.name}`, this.margin, yPosition);
    yPosition += 5;

    // Waypoints if any
    if (data.waypoints && data.waypoints.length > 0) {
      const viaLabel = options.language === 'es' ? 'Vía:' : 'Via:';
      pdf.text(`${viaLabel} ${data.waypoints.map(wp => wp.name).join(', ')}`, this.margin, yPosition);
      yPosition += 5;
    }

    // Vehicle info
    if (options.includeVehicleInfo) {
      const vehicleLabel = options.language === 'es' ? 'Vehículo:' : 'Vehicle:';
      pdf.text(`${vehicleLabel} ${data.vehicle.name} (${data.vehicle.license_plate})`, this.margin, yPosition);
      yPosition += 10;
    }

    // Selected route metrics
    const route = data.selectedRoute;
    const metricsY = yPosition;
    
    // Distance
    const distanceLabel = options.language === 'es' ? 'Distancia:' : 'Distance:';
    pdf.text(`${distanceLabel} ${formatDistance(route.properties.distance)}`, this.margin, metricsY);
    
    // Duration
    const durationLabel = options.language === 'es' ? 'Duración:' : 'Duration:';
    pdf.text(`${durationLabel} ${formatDuration(route.properties.duration)}`, this.margin + 60, metricsY);
    
    // Total cost
    const costLabel = options.language === 'es' ? 'Costo Total:' : 'Total Cost:';
    pdf.text(`${costLabel} ${formatRouteCost(route.properties.total_cost)}`, this.margin + 120, metricsY);
  }

  /**
   * Add map image to PDF
   */
  private async addMapImage(pdf: jsPDF, data: RouteReportData): Promise<void> {
    const mapImage = await this.captureMapScreenshot();
    if (mapImage) {
      const imgWidth = this.pageWidth - (this.margin * 2);
      const imgHeight = (imgWidth * 3) / 4; // 4:3 aspect ratio
      
      // Add new page if needed
      if (pdf.internal.pageSize.height - 100 < imgHeight) {
        pdf.addPage();
      }
      
      pdf.addImage(mapImage, 'PNG', this.margin, 100, imgWidth, imgHeight);
    }
  }

  /**
   * Add complete route details
   */
  private async addCompleteRouteDetails(
    pdf: jsPDF,
    data: RouteReportData,
    options: ReportOptions
  ): Promise<void> {
    pdf.addPage();
    let yPosition = this.margin;

    // Route comparison table
    if (data.routes.length > 1) {
      pdf.setFontSize(14);
      pdf.setFont('helvetica', 'bold');
      const comparisonTitle = options.language === 'es' ? 'Comparación de Rutas' : 'Route Comparison';
      pdf.text(comparisonTitle, this.margin, yPosition);
      yPosition += 15;

      // Table headers
      pdf.setFontSize(9);
      pdf.setFont('helvetica', 'bold');
      const headers = options.language === 'es' 
        ? ['Tipo', 'Distancia', 'Duración', 'Combustible', 'Peajes', 'Total']
        : ['Type', 'Distance', 'Duration', 'Fuel', 'Tolls', 'Total'];
      
      const colWidths = [30, 25, 25, 25, 25, 30];
      let xPosition = this.margin;
      
      headers.forEach((header, index) => {
        pdf.text(header, xPosition, yPosition);
        xPosition += colWidths[index];
      });
      
      yPosition += 8;

      // Table rows
      pdf.setFont('helvetica', 'normal');
      data.routes.forEach(route => {
        xPosition = this.margin;
        const rowData = [
          this.getRouteTypeLabel(route.properties.route_type, options.language),
          formatDistance(route.properties.distance),
          formatDuration(route.properties.duration),
          formatRouteCost(route.properties.fuel_cost),
          formatRouteCost(route.properties.toll_cost),
          formatRouteCost(route.properties.total_cost),
        ];
        
        rowData.forEach((data, index) => {
          pdf.text(data, xPosition, yPosition);
          xPosition += colWidths[index];
        });
        
        yPosition += 6;
      });
    }

    // Cost breakdown
    if (options.includeCostBreakdown) {
      yPosition += 10;
      pdf.setFontSize(12);
      pdf.setFont('helvetica', 'bold');
      const breakdownTitle = options.language === 'es' ? 'Desglose de Costos' : 'Cost Breakdown';
      pdf.text(breakdownTitle, this.margin, yPosition);
      yPosition += 10;

      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'normal');
      
      const route = data.selectedRoute;
      const fuelLabel = options.language === 'es' ? 'Combustible:' : 'Fuel:';
      const tollLabel = options.language === 'es' ? 'Peajes:' : 'Tolls:';
      const totalLabel = options.language === 'es' ? 'Total:' : 'Total:';
      
      pdf.text(`${fuelLabel} ${formatRouteCost(route.properties.fuel_cost)}`, this.margin, yPosition);
      yPosition += 6;
      pdf.text(`${tollLabel} ${formatRouteCost(route.properties.toll_cost)}`, this.margin, yPosition);
      yPosition += 6;
      pdf.setFont('helvetica', 'bold');
      pdf.text(`${totalLabel} ${formatRouteCost(route.properties.total_cost)}`, this.margin, yPosition);
    }

    // Toll details
    if (options.includeTollDetails && data.tollPoints && data.tollPoints.length > 0) {
      yPosition += 15;
      pdf.setFontSize(12);
      pdf.setFont('helvetica', 'bold');
      const tollTitle = options.language === 'es' ? 'Detalles de Peajes' : 'Toll Details';
      pdf.text(tollTitle, this.margin, yPosition);
      yPosition += 10;

      pdf.setFontSize(9);
      pdf.setFont('helvetica', 'normal');
      
      data.tollPoints.forEach(toll => {
        pdf.text(`• ${toll.data.name} - ${formatRouteCost(toll.data.cost)}`, this.margin, yPosition);
        yPosition += 5;
      });
    }
  }

  /**
   * Add simple route details
   */
  private addSimpleRouteDetails(
    pdf: jsPDF,
    data: RouteReportData,
    options: ReportOptions
  ): void {
    let yPosition = 180;

    pdf.setFontSize(12);
    pdf.setFont('helvetica', 'bold');
    const detailsTitle = options.language === 'es' ? 'Detalles de la Ruta' : 'Route Details';
    pdf.text(detailsTitle, this.margin, yPosition);
    yPosition += 10;

    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');

    const route = data.selectedRoute;
    const details = [
      `${options.language === 'es' ? 'Tipo de ruta:' : 'Route type:'} ${this.getRouteTypeLabel(route.properties.route_type, options.language)}`,
      `${options.language === 'es' ? 'Distancia total:' : 'Total distance:'} ${formatDistance(route.properties.distance)}`,
      `${options.language === 'es' ? 'Tiempo estimado:' : 'Estimated time:'} ${formatDuration(route.properties.duration)}`,
      `${options.language === 'es' ? 'Costo de combustible:' : 'Fuel cost:'} ${formatRouteCost(route.properties.fuel_cost)}`,
      `${options.language === 'es' ? 'Costo de peajes:' : 'Toll cost:'} ${formatRouteCost(route.properties.toll_cost)}`,
      `${options.language === 'es' ? 'Costo total:' : 'Total cost:'} ${formatRouteCost(route.properties.total_cost)}`,
    ];

    details.forEach(detail => {
      pdf.text(detail, this.margin, yPosition);
      yPosition += 6;
    });
  }

  /**
   * Add route comparison
   */
  private async addRouteComparison(
    pdf: jsPDF,
    data: RouteReportData,
    options: ReportOptions
  ): Promise<void> {
    // Implementation for comparison format
    await this.addCompleteRouteDetails(pdf, data, options);
  }

  /**
   * Add mobile header
   */
  private async addMobileHeader(
    pdf: jsPDF,
    data: RouteReportData,
    options: ReportOptions
  ): Promise<void> {
    let yPosition = 15;

    pdf.setFontSize(14);
    pdf.setFont('helvetica', 'bold');
    const title = options.language === 'es' ? 'Hoja de Ruta' : 'Route Sheet';
    pdf.text(title, 10, yPosition);
    
    yPosition += 8;
    pdf.setFontSize(8);
    pdf.setFont('helvetica', 'normal');
    pdf.text(data.calculatedAt.toLocaleDateString(), 10, yPosition);
  }

  /**
   * Add compact route info for mobile
   */
  private addCompactRouteInfo(
    pdf: jsPDF,
    data: RouteReportData,
    options: ReportOptions
  ): void {
    let yPosition = 35;

    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'bold');
    
    // Origin to destination
    pdf.text(`${data.origin.name}`, 10, yPosition);
    yPosition += 5;
    pdf.text('↓', 10, yPosition);
    yPosition += 5;
    pdf.text(`${data.destination.name}`, 10, yPosition);
    yPosition += 10;

    // Key metrics
    const route = data.selectedRoute;
    pdf.setFontSize(9);
    pdf.setFont('helvetica', 'normal');
    
    pdf.text(`${formatDistance(route.properties.distance)} • ${formatDuration(route.properties.duration)}`, 10, yPosition);
    yPosition += 5;
    pdf.text(`${formatRouteCost(route.properties.total_cost)}`, 10, yPosition);
  }

  /**
   * Add essential details for mobile
   */
  private addEssentialDetails(
    pdf: jsPDF,
    data: RouteReportData,
    options: ReportOptions
  ): void {
    let yPosition = 70;

    const route = data.selectedRoute;
    
    pdf.setFontSize(8);
    pdf.setFont('helvetica', 'normal');
    
    const details = [
      `Fuel: ${formatRouteCost(route.properties.fuel_cost)}`,
      `Tolls: ${formatRouteCost(route.properties.toll_cost)}`,
      `Vehicle: ${data.vehicle.name}`,
    ];

    details.forEach(detail => {
      pdf.text(detail, 10, yPosition);
      yPosition += 4;
    });
  }

  /**
   * Add footer to PDF
   */
  private addFooter(
    pdf: jsPDF,
    data: RouteReportData,
    options: ReportOptions
  ): void {
    const pageCount = pdf.internal.getNumberOfPages();
    
    for (let i = 1; i <= pageCount; i++) {
      pdf.setPage(i);
      pdf.setFontSize(8);
      pdf.setFont('helvetica', 'normal');
      
      // Page number
      pdf.text(
        `${options.language === 'es' ? 'Página' : 'Page'} ${i} ${options.language === 'es' ? 'de' : 'of'} ${pageCount}`,
        this.pageWidth - this.margin - 20,
        this.pageHeight - 10
      );
      
      // Generated by
      pdf.text(
        options.language === 'es' ? 'Generado por Route Optimizer' : 'Generated by Route Optimizer',
        this.margin,
        this.pageHeight - 10
      );
    }
  }

  /**
   * Generate filename for the report
   */
  private generateFileName(
    data: RouteReportData,
    options: ReportOptions,
    prefix: string = 'route'
  ): string {
    const date = data.calculatedAt.toISOString().split('T')[0];
    const origin = data.origin.name.replace(/[^a-zA-Z0-9]/g, '_');
    const destination = data.destination.name.replace(/[^a-zA-Z0-9]/g, '_');
    
    return `${prefix}_report_${origin}_to_${destination}_${date}.pdf`;
  }

  /**
   * Get route type label in specified language
   */
  private getRouteTypeLabel(type: string, language: 'es' | 'en'): string {
    const labels = {
      fastest: language === 'es' ? 'Más Rápida' : 'Fastest',
      shortest: language === 'es' ? 'Más Corta' : 'Shortest',
      recommended: language === 'es' ? 'Recomendada' : 'Recommended',
    };
    
    return labels[type as keyof typeof labels] || type;
  }

  /**
   * Get default report options
   */
  private getDefaultOptions(): ReportOptions {
    return {
      format: 'complete',
      includeMap: true,
      includeRouteDetails: true,
      includeCostBreakdown: true,
      includeTollDetails: true,
      includeVehicleInfo: true,
      language: 'es',
    };
  }
}

// Create and export singleton instance
export const reportService = new ReportService();