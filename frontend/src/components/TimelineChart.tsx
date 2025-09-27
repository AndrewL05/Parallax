import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';
import type { TimelinePoint } from '../types/api';

interface TimelineChartProps {
  data: TimelinePoint[];
  title: string;
  color: string;
}

const TimelineChart: React.FC<TimelineChartProps> = ({ data, title, color }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data || data.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 40, right: 80, bottom: 60, left: 80 };
    const width = 600 - margin.left - margin.right;
    const height = 350 - margin.bottom - margin.top;

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Scales
    const xScale = d3.scaleLinear()
      .domain([1, 10])
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain([0, (d3.max(data, d => d.salary || 0) || 0) * 1.1])
      .range([height, 0]);

    const happinessScale = d3.scaleLinear()
      .domain([0, 10])
      .range([height, 0]);

    // Line generators
    const salaryLine = d3.line<TimelinePoint>()
      .x(d => xScale(d.year))
      .y(d => yScale(d.salary || 0))
      .curve(d3.curveMonotoneX);

    const happinessLine = d3.line<TimelinePoint>()
      .x(d => xScale(d.year))
      .y(d => happinessScale(d.happiness_score))
      .curve(d3.curveMonotoneX);

    // Add grid lines
    g.append("g")
      .attr("class", "grid")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale)
        .tickSize(-height)
        .tickFormat(() => "")
      )
      .style("stroke-dasharray", "3,3")
      .style("opacity", 0.3);

    g.append("g")
      .attr("class", "grid")
      .call(d3.axisLeft(yScale)
        .tickSize(-width)
        .tickFormat(() => "")
      )
      .style("stroke-dasharray", "3,3")
      .style("opacity", 0.3);

    // Add axes
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale)
        .tickFormat(d => `Year ${d}`)
      )
      .selectAll("text")
      .style("font-size", "12px")
      .style("fill", "#6B7280");

    g.append("g")
      .call(d3.axisLeft(yScale)
        .tickFormat(d => `$${((d as number)/1000)}k`)
      )
      .selectAll("text")
      .style("font-size", "12px")
      .style("fill", "#6B7280");

    // Add happiness axis on the right
    g.append("g")
      .attr("transform", `translate(${width},0)`)
      .call(d3.axisRight(happinessScale)
        .tickFormat(d => `${d}/10`)
      )
      .selectAll("text")
      .style("font-size", "12px")
      .style("fill", "#EF4444");

    // Add salary line with gradient
    const gradient = g.append("defs")
      .append("linearGradient")
      .attr("id", `gradient-${title.replace(/\s/g, '')}`)
      .attr("gradientUnits", "userSpaceOnUse")
      .attr("x1", 0).attr("y1", height)
      .attr("x2", 0).attr("y2", 0);

    gradient.append("stop")
      .attr("offset", "0%")
      .attr("stop-color", color)
      .attr("stop-opacity", 0.1);

    gradient.append("stop")
      .attr("offset", "100%")
      .attr("stop-color", color)
      .attr("stop-opacity", 0.8);

    // Add area under salary line
    const area = d3.area<TimelinePoint>()
      .x(d => xScale(d.year))
      .y0(height)
      .y1(d => yScale(d.salary || 0))
      .curve(d3.curveMonotoneX);

    g.append("path")
      .datum(data)
      .attr("fill", `url(#gradient-${title.replace(/\s/g, '')})`)
      .attr("d", area);

    // Add salary line
    g.append("path")
      .datum(data)
      .attr("fill", "none")
      .attr("stroke", color)
      .attr("stroke-width", 3)
      .attr("d", salaryLine);

    // Add happiness line
    g.append("path")
      .datum(data)
      .attr("fill", "none")
      .attr("stroke", "#EF4444")
      .attr("stroke-width", 2)
      .attr("stroke-dasharray", "5,5")
      .attr("d", happinessLine);

    // Add data points
    g.selectAll(".salary-dot")
      .data(data)
      .enter().append("circle")
      .attr("class", "salary-dot")
      .attr("cx", d => xScale(d.year))
      .attr("cy", d => yScale(d.salary || 0))
      .attr("r", 5)
      .attr("fill", color)
      .attr("stroke", "white")
      .attr("stroke-width", 2)
      .style("cursor", "pointer")
      .on("mouseover", function(event: MouseEvent, d: TimelinePoint) {
        // Create tooltip
        const tooltip = d3.select("body").append("div")
          .attr("class", "d3-tooltip")
          .style("position", "absolute")
          .style("background", "rgba(0, 0, 0, 0.8)")
          .style("color", "white")
          .style("padding", "8px")
          .style("border-radius", "4px")
          .style("font-size", "12px")
          .style("pointer-events", "none")
          .style("opacity", 0);

        tooltip.transition()
          .duration(200)
          .style("opacity", 1);

        tooltip.html(`
          <strong>Year ${d.year}</strong><br/>
          Salary: $${d.salary?.toLocaleString()}<br/>
          Happiness: ${d.happiness_score}/10<br/>
          ${d.major_event ? `Event: ${d.major_event}` : ''}
        `)
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 28) + "px");
      })
      .on("mouseout", function() {
        d3.selectAll(".d3-tooltip").remove();
      });

    // Add happiness dots
    g.selectAll(".happiness-dot")
      .data(data)
      .enter().append("circle")
      .attr("class", "happiness-dot")
      .attr("cx", d => xScale(d.year))
      .attr("cy", d => happinessScale(d.happiness_score))
      .attr("r", 4)
      .attr("fill", "#EF4444")
      .attr("stroke", "white")
      .attr("stroke-width", 2);

    // Add labels with better positioning
    g.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left + 20)
      .attr("x", 0 - (height / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .style("font-size", "14px")
      .style("font-weight", "bold")
      .style("fill", color)
      .text("Annual Salary");

    g.append("text")
      .attr("transform", `translate(${width + margin.right - 20}, ${height / 2}) rotate(90)`)
      .style("text-anchor", "middle")
      .style("font-size", "14px")
      .style("font-weight", "bold")
      .style("fill", "#EF4444")
      .text("Happiness Score");

    g.append("text")
      .attr("x", width / 2)
      .attr("y", 0 - 10)
      .attr("text-anchor", "middle")
      .style("font-size", "18px")
      .style("font-weight", "bold")
      .style("fill", "#374151")
      .text(title);

    // Add legend
    const legend = g.append("g")
      .attr("transform", `translate(${width - 140}, 20)`);

    legend.append("line")
      .attr("x1", 0)
      .attr("x2", 20)
      .attr("y1", 0)
      .attr("y2", 0)
      .attr("stroke", color)
      .attr("stroke-width", 3);

    legend.append("text")
      .attr("x", 25)
      .attr("y", 0)
      .attr("dy", "0.35em")
      .style("font-size", "12px")
      .style("fill", "#374151")
      .text("Salary");

    legend.append("line")
      .attr("x1", 0)
      .attr("x2", 20)
      .attr("y1", 20)
      .attr("y2", 20)
      .attr("stroke", "#EF4444")
      .attr("stroke-width", 2)
      .attr("stroke-dasharray", "5,5");

    legend.append("text")
      .attr("x", 25)
      .attr("y", 20)
      .attr("dy", "0.35em")
      .style("font-size", "12px")
      .style("fill", "#374151")
      .text("Happiness");

  }, [data, title, color]);

  return <svg ref={svgRef} width="600" height="350" className="timeline-chart"></svg>;
};

export default TimelineChart;