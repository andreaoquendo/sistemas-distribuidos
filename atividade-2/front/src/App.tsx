import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Navbar } from "./components/Navbar";
import { GlobalStyle } from "./styles";
import Promocoes from "./pages/Promocoes";
import Consulta from "./pages/Consulta";

function App() {
  return (
    <BrowserRouter>
      <GlobalStyle />
      <Navbar />
      <Routes>
        <Route path="/" element={<Consulta />} />
        {/* <Route path="/reserva" element={<Reserva />} />
        <Route path="/status" element={<Status />} /> */}
        <Route path="/promocoes" element={<Promocoes />} />
        {/* <Route path="/admin" element={<Admin />} /> */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;
