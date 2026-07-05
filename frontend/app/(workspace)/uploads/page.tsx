import { redirect } from "next/navigation";

export const metadata = { title: "Uploads" };

export default function UploadsPage() {
  redirect("/libraries");
}
