import * as d3 from "d3";

const data = {
  title: "root",
  children: [
    {
      id: 1,
      title: "Project A",
      description: "Description of Project A",
      children: [
        {
          id: 2,
          title: "Subproject A1",
          description: "Description of Subproject A1",
        },
        {
          id: 3,
          title: "Subproject A2",
          description: "Description of Subproject A2",
        },
      ],
    },
    { id: 4, title: "Project B", description: "Description of Project B" },
    {
      id: 5,
      title: "Project C",
      description: "Description of Project C",
      children: [
        {
          id: 6,
          title: "Subproject C1",
          description: "Description of Subproject C1",
        },
        {
          id: 7,
          title: "Subproject C2",
          description: "Description of Subproject C2",
        },
      ],
    },
  ],
};

export default function Work() {
  const width = 1154;
  const height = 1154;
  // Specify the color scale.
  const color = d3.scaleOrdinal(
    data.children.map((d) => d.title),
    d3.schemeTableau10
  );

  // Compute the layout.
  const root = d3
    .treemap()
    .tile(d3.treemapSquarify)
    .size([width, height])
    .padding(1)
    .round(true);

  return (
    <div className="container">
      <h1>Work</h1>
      <p>Work in progress...</p>
    </div>
  );
}
