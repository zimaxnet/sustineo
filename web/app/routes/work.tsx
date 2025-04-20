import * as d3 from "d3";
import styles from "./work.module.scss";
import { useRef } from "react";
import useDimensions from "store/usedimensions";
import { v4 as uuidv4 } from "uuid";

interface DataNode {
  id: string;
  title: string;
  description?: string;
  value: number;
  children: DataNode[];
}

const data: DataNode = {
  id: uuidv4(),
  title: "root",
  value: 1,
  children: [
    {
      id: uuidv4(),
      title: "Project A",
      description: "Description of Project A",
      value: 1,
      children: [
        {
          id: uuidv4(),
          title: "Subproject A1",
          description: "Description of Subproject A1",
          value: 1,
          children: [],
        },
        {
          id: uuidv4(),
          title: "Subproject A2",
          description: "Description of Subproject A2",
          value: 1,
          children: [
            {
              id: uuidv4(),
              title: "Subproject A2.1",
              description: "Description of Subproject A2.1",
              value: 1,
              children: [],
            },
            {
              id: uuidv4(),
              title: "Subproject A2.2",
              description: "Description of Subproject A2.2",
              value: 1,
              children: [],
            },
          ],
        },
      ],
    },
    {
      id: uuidv4(),
      title: "Project B",
      description: "Description of Project B",
      value: 1,
      children: [
        {
          id: uuidv4(),
          title: "Subproject B1",
          description: "Description of Subproject B1",
          value: 1,
          children: [],
        },
        {
          id: uuidv4(),
          title: "Subproject B2",
          description: "Description of Subproject B2",
          value: 1,
          children: [],
        },
      ],
    },
    {
      id: uuidv4(),
      title: "Project C",
      description: "Description of Project C",
      value: 1,
      children: [
        {
          id: uuidv4(),
          title: "Subproject C1",
          description: "Description of Subproject C1",
          value: 1,
          children: [],
        },
        {
          id: uuidv4(),
          title: "Subproject C2",
          description: "Description of Subproject C2",
          value: 1,
          children: [
            {
              id: uuidv4(),
              title: "Subproject C2.1",
              description: "Description of Subproject C2.1",
              value: 1,
              children: [],
            },
            {
              id: uuidv4(),
              title: "Subproject C2.2",
              description: "Description of Subproject C2.2",
              value: 1,
              children: [],
            },
          ],
        },
      ],
    },
    {
      id: uuidv4(),
      title: "Project D",
      description: "Description of Project D",
      value: 1,
      children: [
        {
          id: uuidv4(),
          title: "Subproject D1",
          description: "Description of Subproject D1",
          value: 1,
          children: [],
        },
        {
          id: uuidv4(),
          title: "Subproject D2",
          description: "Description of Subproject D2",
          value: 1,
          children: [],
        },
        {
          id: uuidv4(),
          title: "Subproject D3",
          description: "Description of Subproject D3",
          value: 1,
          children: [],
        },
        {
          id: uuidv4(),
          title: "Subproject D4",
          description: "Description of Subproject D4",
          value: 1,
          children: [
            {
              id: uuidv4(),
              title: "Subproject D4.1",
              description: "Description of Subproject D4.1",
              value: 1,
              children: [],
            },
            {
              id: uuidv4(),
              title: "Subproject D4.2",
              description: "Description of Subproject D4.2",
              value: 1,
              children: [],
            },
          ],
        },
      ],
    },
    {
      id: uuidv4(),
      title: "Project E",
      description: "Description of Project E",
      value: 1,
      children: [
        {
          id: uuidv4(),
          title: "Subproject E1",
          description: "Description of Subproject E1",
          value: 1,
          children: [],
        },
        {
          id: uuidv4(),
          title: "Subproject E2",
          description: "Description of Subproject E2",
          value: 1,
          children: [
            {
              id: uuidv4(),
              title: "Subproject E2.1",
              description: "Description of Subproject E2.1",
              value: 1,
              children: [],
            },
            {
              id: uuidv4(),
              title: "Subproject E2.2",
              description: "Description of Subproject E2.2",
              value: 1,
              children: [
                {
                  id: uuidv4(),
                  title: "Subproject E2.2.1",
                  description: "Description of Subproject E2.2.1",
                  value: 1,
                  children: [],
                },
                {
                  id: uuidv4(),
                  title: "Subproject E2.2.2",
                  description: "Description of Subproject E2.2.2",
                  value: 1,
                  children: [],
                },
              ],
            },
          ],
        },
      ],
    },
  ],
};



export default function Work() {
  const chartRef = useRef<HTMLDivElement>(null);
  const dms = useDimensions(chartRef, {
    marginLeft: 20,
    marginRight: 20,
    marginTop: 20,
    marginBottom: 20,
  });
  
  // Specify the color scale.
  const color = d3.scaleOrdinal(
    data.children.map((d) => d.title),
    d3.schemeTableau10
  );

  const getColor = (d: d3.HierarchyRectangularNode<DataNode>) => {
    const t = d.ancestors().reverse()[1];
    return color(t.data.title);
  };

  const hierarchy = d3
    .hierarchy(data)
    .sum((d) => d.value)
    .sort((a, b) => (b.value || 0) - (a.value || 0));

  const root = d3
    .treemap<DataNode>()
    .tile(d3.treemapBinary)
    .size([dms.boundedWidth, dms.boundedHeight])
    .padding(1)
    .round(false)(hierarchy);

  //console.log(root.leaves());

  return (
    <div className={styles.container} ref={chartRef}>
      <svg
        width={dms.width}
        height={dms.height}
        className={styles.treemap}
      >
        <g
          transform={`translate(${[dms.marginLeft, dms.marginTop].join(",")})`}
          height={dms.boundedHeight}
          width={dms.boundedWidth}
        >
          {root.leaves().map((d, i) => (
            <g
              key={i}
              transform={`translate(${d.x0},${d.y0})`}
              onClick={() => {
                console.log(d.data);
              }}
              onMouseOver={() => {
                const rect = document.getElementById(i + "_rect");
                if (rect) {
                  rect.setAttribute("opacity", "0.5");
                }
              }}
              onMouseOut={() => {
                const rect = document.getElementById(i + "_rect");
                if (rect) {
                  rect.setAttribute("opacity", "1");
                }
              }}
              className={styles.item}
            >
              <rect
                id={i + "_rect"}
                width={d.x1 - d.x0}
                height={d.y1 - d.y0}
                fill={getColor(d)}
              />

              <text x={3} y={17} style={{ fontSize: "1em", fill: "white" }}>
                <tspan x={3}>
                  {d
                    .ancestors()
                    .slice(0, -1)
                    .reverse()
                    .map((d) => d.data.title.replace(" ", "-"))
                    .join(".")}
                </tspan>
                <tspan x={3} dy="1.2em">
                  {d.data.value}
                </tspan>
              </text>
            </g>
          ))}
        </g>
      </svg>
    </div>
  );
}
