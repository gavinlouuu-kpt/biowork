import { useMemo } from "react";
import { createColumnHelper, flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table";
import { Block, Elem } from "../../utils/bem";
import "./SegmentationMetricsTable.scss";

const columnHelper = createColumnHelper();

export const SegmentationMetricsTable = ({ rows }) => {
  const data = Array.isArray(rows) ? rows : [];

  const columns = useMemo(
    () => [
      columnHelper.accessor("image_filename", {
        header: "Image",
        cell: (info) => info.getValue() ?? "",
      }),
      columnHelper.accessor("task_id", {
        header: "Task ID",
        cell: (info) => info.getValue(),
      }),
      columnHelper.accessor("annotation_id", {
        header: "Annotation ID",
        cell: (info) => info.getValue(),
      }),
      columnHelper.accessor("region_id", {
        header: "Region ID",
        cell: (info) => info.getValue(),
      }),
      columnHelper.accessor("label", {
        header: "Label",
        cell: (info) => info.getValue() ?? "",
      }),
      columnHelper.accessor("shape_type", {
        header: "Shape",
        cell: (info) => info.getValue() ?? "",
      }),
      columnHelper.accessor("bbox_x_px", {
        header: "BBox X (px)",
        cell: (info) => info.getValue(),
      }),
      columnHelper.accessor("bbox_y_px", {
        header: "BBox Y (px)",
        cell: (info) => info.getValue(),
      }),
      columnHelper.accessor("x_length_px", {
        header: "Width (px)",
        cell: (info) => info.getValue(),
      }),
      columnHelper.accessor("y_length_px", {
        header: "Height (px)",
        cell: (info) => info.getValue(),
      }),
      columnHelper.accessor("area_px", {
        header: "Area (px²)",
        cell: (info) => info.getValue(),
      }),
      columnHelper.accessor("mean_gray", {
        header: "Mean gray",
        cell: (info) => formatNumber(info.getValue()),
      }),
      columnHelper.accessor("mean_r", {
        header: "Mean R",
        cell: (info) => formatNumber(info.getValue()),
      }),
      columnHelper.accessor("mean_g", {
        header: "Mean G",
        cell: (info) => formatNumber(info.getValue()),
      }),
      columnHelper.accessor("mean_b", {
        header: "Mean B",
        cell: (info) => formatNumber(info.getValue()),
      }),
      columnHelper.accessor("polygon_points_px", {
        header: "Polygon points (px)",
        cell: (info) => {
          const raw = info.getValue();
          if (!raw) return "";
          const text = typeof raw === "string" ? raw : JSON.stringify(raw);
          const shortened = text.length > 120 ? `${text.slice(0, 117)}...` : text;
          return <span title={text}>{shortened}</span>;
        },
      }),
    ],
    [],
  );

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <Block name="segmetrics-table">
      <Elem name="scroll">
        <table className="segmetrics-table__table">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th key={header.id}>
                    {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </Elem>
    </Block>
  );
};

const formatNumber = (value) => {
  if (value === null || value === undefined) return "";
  if (typeof value !== "number") return value;
  return Number.isFinite(value) ? value.toFixed(2) : value;
};


