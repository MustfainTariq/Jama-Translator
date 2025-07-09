import LeaveButton from "@/components/controls/leave-button";

export default function ListenerControls() {
  return (
    <div className="flex items-center justify-center gap-4">
      {/* Hide CC button and language picker for iframe display */}
      {/* <CaptionsToggle /> */}
      {/* <LanguageSelect /> */}
      <LeaveButton />
    </div>
  );
}
