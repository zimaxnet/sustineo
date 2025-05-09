import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("/chat", "routes/chat.tsx"), 
  route("/favicon.svg", "favicon.tsx"), 
  route("/.well-known/appspecific/com.chrome.devtools.json", "none.tsx")] satisfies RouteConfig;
