import { api } from "./api";

export interface Course {
  id: string;
  code: string;
  title: string;
  level: string;
  semester: string;
  units: number;
  description: string | null;
}

export interface Lecturer {
  id: string;
  full_name: string;
  title: string | null;
  email: string | null;
  office: string | null;
  office_hours: string | null;
  biography: string | null;
}

export interface Department {
  id: string;
  name: string;
}

export const listCourses = () => api.get<Course[]>("/courses").then((r) => r.data);
export const createCourse = (payload: Record<string, unknown>) => api.post<Course>("/courses", payload).then((r) => r.data);
export const deleteCourse = (id: string) => api.delete(`/courses/${id}`);

export const listLecturers = () => api.get<Lecturer[]>("/lecturers").then((r) => r.data);
export const createLecturer = (payload: Record<string, unknown>) => api.post<Lecturer>("/lecturers", payload).then((r) => r.data);
export const deleteLecturer = (id: string) => api.delete(`/lecturers/${id}`);

export const listDepartments = () => api.get<Department[]>("/departments").then((r) => r.data);
