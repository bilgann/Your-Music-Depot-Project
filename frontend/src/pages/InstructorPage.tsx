'use client'

import React from "react";

export type Instructor = {
  id: string
  fullName: string
  instrument: string
  skillLevel: number
  status: string
  availability: string
  payRate: number
}

function LoadingRow() {
  return (
    <tr className="animate-pulse">
      {Array.from({ length: 8}).map((_, i) => (
        <td key={i} className="p-4 border">
          <div className="h-4 bg-gray-300 rounded w-full"></div>

        </td>
      ))}
    </tr>
  )
}

type RowProps = {
  instructor: Instructor
  onEdit?: (id: string) => void
  onDelete?: (id: string) => void
}

function InstructorRow({ instructor, onEdit, onDelete}: RowProps) {
  return (
    <tr className="">

      {/* List of atrributes */}

      <td className="">{instructor.fullName}</td>
      <td className="">{instructor.instrument}</td>
      <td className="">{instructor.skillLevel}</td>
      <td className="">{instructor.status}</td>
      <td className="">{instructor.availability}</td>

      {/* Edit Button */}

      <td className="">
        <button
          onClick={() => onEdit?.(instructor.id)}
          className=""
        >
          Edit
          </button>  
      </td>

      {/* Delete Button */}

      <td className="">
        <button
          onClick={() => onDelete?.(instructor.id)}
          className=""
        >
          Edit
          </button>  

        <td className="">${instructor.payRate}</td>

      </td>
    </tr>
  )
}


type Props = {
  instructor?: Instructor[]
  loading?: boolean
  onEdit?: (id: string) => void
  onDelete?: (id: string) => void
  onAdd?: () => void
}

export default function InstructorPage({

  instructor = [],
  loading = false,
  onEdit,
  onDelete,
  onAdd

}: Props) {

  return (

    <div className="w-full p-6">

        {/* Table */}
        <div className="w-full border border-purple-500">

          <table className="w-full border-collapse">

            {/* Header */}
            <thead>
              <tr className="bg-zinc-900 text-white text-sm">
                <th className="p-4 border">Full Name</th>
                <th className="p-4 border">Instrument</th>
                <th className="p-4 border">Skill Level</th>
                <th className="p-4 border">Status</th>
                <th className="p-4 border">Availability</th>
                <th className="p-4 border">Edit</th>
                <th className="p-4 border">Delete</th>
                <th className="p-4 border">Pay Rate</th>
              </tr>
            </thead>

            {/* Body */}
            <tbody>

              {loading && (
                <>
                  <LoadingRow />
                  <LoadingRow />
                  <LoadingRow />
                  <LoadingRow />
                </>
              )}

              {!loading && instructor.map((instructor) => (
                <InstructorRow
                  key={instructor.id}
                  instructor={instructor}
                  onEdit={onEdit}
                  onDelete={onDelete}
                />
              ))}

              {!loading && instructor.length === 0 && (
                <tr>
                  <td colSpan={8} className="p-6 text-center text-gray-500">
                    No instructors found
                  </td>
                </tr>
              )}

            </tbody>

          </table>
        </div>

        {/* Add Button */}
        <div className="w-full bg-zinc-900 flex justify-center items-center py-10">
          <button
            onClick={onAdd}
            className="text-white text-3xl hover:scale-110 transition"
          >
            +
          </button>
        </div>

      </div>
  )
}