"use client";

import MicToggle from "@/components/controls/mic-toggle";
import LeaveButton from "@/components/controls/leave-button";
// Remove these imports to hide CC button and language picker
// import CaptionsToggle from "@/components/controls/captions-toggle";
// import LanguageSelect from "@/components/controls/language-select";
import DeviceSelector from "@/components/controls/device-selector";

export default function HostControls() {
  return (
    <div className="flex items-center justify-center gap-4">
      <DeviceSelector />
      <MicToggle />
      {/* Hide CC button and language picker for iframe display */}
      {/* <CaptionsToggle /> */}
      {/* <LanguageSelect /> */}
      <LeaveButton />
    </div>
  );
}
