import { BrowserRouter, Routes } from "react-router-dom";
import { Navbar } from "./components/Navbar";
import { GlobalStyle } from "./styles";

function App() {
  return (
    <BrowserRouter>
      <GlobalStyle />
      <Navbar />
      <Routes>
        {/* <Route path="/" element={<Consulta />} />
        <Route path="/reserva" element={<Reserva />} />
        <Route path="/status" element={<Status />} />
        <Route path="/promocoes" element={<Promocoes />} />
        <Route path="/admin" element={<Admin />} /> */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;
