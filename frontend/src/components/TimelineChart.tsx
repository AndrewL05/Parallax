import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import type { TimelinePoint } from '../types/api';

interface TimelineChartProps {
  data: TimelinePoint[];
  title: string;
  color: string;
}

const TimelineChart: React.FC<TimelineChartProps> = ({ data, title, color }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const [dims, setDims] = useState({ w: 0, h: 0 });

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const obs = new ResizeObserver((entries) => {
      const w = entries[0].contentRect.width;
      setDims({ w, h: Math.min(300, w * 0.5) });
    });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  useEffect(() => {
    if (!data?.length || !dims.w) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const m = { top: 16, right: 48, bottom: 32, left: 52 };
    const w = dims.w - m.left - m.right;
    const h = dims.h - m.top - m.bottom;
    if (w <= 0 || h <= 0) return;

    const g = svg.append("g").attr("transform", `translate(${m.left},${m.top})`);

    const x = d3.scaleLinear().domain([1, 10]).range([0, w]);
    const y = d3.scaleLinear().domain([0, (d3.max(data, d => d.salary || 0) || 1) * 1.12]).range([h, 0]);
    const yH = d3.scaleLinear().domain([0, 10]).range([h, 0]);

    // Grid
    g.append("g").call(d3.axisLeft(y).tickSize(-w).tickFormat(() => ""))
      .call(g => g.select(".domain").remove())
      .call(g => g.selectAll(".tick line").attr("stroke", "#f5f5f4").attr("stroke-dasharray", "2,2"));

    // X axis
    g.append("g").attr("transform", `translate(0,${h})`)
      .call(d3.axisBottom(x).ticks(10).tickFormat(d => `${d}`))
      .call(g => g.select(".domain").attr("stroke", "#e7e5e4"))
      .selectAll("text").style("font-size", "10px").style("fill", "#a8a29e");

    // Y axis salary
    g.append("g").call(d3.axisLeft(y).ticks(5).tickFormat(d => `$${((d as number) / 1000).toFixed(0)}k`))
      .call(g => g.select(".domain").remove())
      .selectAll("text").style("font-size", "10px").style("fill", "#a8a29e");

    // Y axis happiness
    g.append("g").attr("transform", `translate(${w},0)`)
      .call(d3.axisRight(yH).ticks(5).tickFormat(d => `${d}`))
      .call(g => g.select(".domain").remove())
      .selectAll("text").style("font-size", "10px").style("fill", "#d6d3d1");

    // Area
    const gradId = `a-${title.replace(/\s/g, '')}`;
    const defs = g.append("defs");
    const grad = defs.append("linearGradient").attr("id", gradId)
      .attr("gradientUnits", "userSpaceOnUse").attr("x1", 0).attr("y1", h).attr("x2", 0).attr("y2", 0);
    grad.append("stop").attr("offset", "0%").attr("stop-color", color).attr("stop-opacity", 0);
    grad.append("stop").attr("offset", "100%").attr("stop-color", color).attr("stop-opacity", 0.08);

    g.append("path").datum(data)
      .attr("fill", `url(#${gradId})`)
      .attr("d", d3.area<TimelinePoint>().x(d => x(d.year)).y0(h).y1(d => y(d.salary || 0)).curve(d3.curveMonotoneX));

    // Salary line
    g.append("path").datum(data)
      .attr("fill", "none").attr("stroke", color).attr("stroke-width", 2)
      .attr("d", d3.line<TimelinePoint>().x(d => x(d.year)).y(d => y(d.salary || 0)).curve(d3.curveMonotoneX));

    // Happiness line
    g.append("path").datum(data)
      .attr("fill", "none").attr("stroke", "#d6d3d1").attr("stroke-width", 1)
      .attr("stroke-dasharray", "3,3")
      .attr("d", d3.line<TimelinePoint>().x(d => x(d.year)).y(d => yH(d.happiness_score)).curve(d3.curveMonotoneX));

    // Dots
    g.selectAll(".sd").data(data).enter().append("circle")
      .attr("cx", d => x(d.year)).attr("cy", d => y(d.salary || 0))
      .attr("r", 3.5).attr("fill", color).attr("stroke", "white").attr("stroke-width", 1.5)
      .style("cursor", "pointer")
      .on("mouseover", (event: MouseEvent, d: TimelinePoint) => {
        d3.select("body").selectAll(".d3-tooltip").remove();
        const tip = d3.select("body").append("div").attr("class", "d3-tooltip").style("opacity", 0);
        tip.transition().duration(120).style("opacity", 1);
        tip.html(
          `<strong>Year ${d.year}</strong><br/>$${d.salary?.toLocaleString()}<br/>${d.happiness_score}/10 happiness` +
          (d.major_event ? `<br/><span style="color:#a8a29e">${d.major_event}</span>` : '')
        ).style("left", `${event.pageX + 10}px`).style("top", `${event.pageY - 10}px`);
      })
      .on("mouseout", () => d3.selectAll(".d3-tooltip").remove());

    g.selectAll(".hd").data(data).enter().append("circle")
      .attr("cx", d => x(d.year)).attr("cy", d => yH(d.happiness_score))
      .attr("r", 2.5).attr("fill", "#d6d3d1").attr("stroke", "white").attr("stroke-width", 1);

  }, [data, title, color, dims]);

  return (
    <div ref={containerRef} className="w-full">
      <svg ref={svgRef} width={dims.w} height={dims.h} viewBox={`0 0 ${dims.w} ${dims.h}`} />
    </div>
  );
};

export default TimelineChart;
